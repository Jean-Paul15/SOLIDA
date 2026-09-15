import uuid
from dataclasses import dataclass

from solida.application.use_cases.scorer_demande import ScorerDemande
from solida.domain.errors import (
    IdentiteSocietaireInvalide,
    ProduitIntrouvable,
    SocietaireIntrouvable,
)
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.ports.decisions import DecisionRepository
from solida.domain.ports.demande_societaire import DemandeSocietaireRepository
from solida.domain.ports.grille import GrilleRepository
from solida.domain.ports.notification_sender import NotificationSender
from solida.domain.rules.jeton_societaire import verifier_jeton
from solida.domain.rules.pre_verification import PreVerification, calculer_pre_verification
from solida.domain.values.demande import ActualisationSituation, DemandeScoring
from solida.domain.values.demande_societaire import DemandeSocietaireACreer
from solida.domain.values.montant import Montant

AGENT_ID_PORTAIL = "portail-societaire"
AGENT_NOM_PORTAIL = "Portail sociétaire"


@dataclass(frozen=True)
class ResultatDemandeSocietaire:
    demande_id: str
    pre_verification: PreVerification


@dataclass(frozen=True)
class ProcessSocietaireDemande:
    core_sim_reader: CoreSimReader
    scorer_demande: ScorerDemande
    demande_societaire_repository: DemandeSocietaireRepository
    decision_repository: DecisionRepository
    notification_sender: NotificationSender
    grille_repository: GrilleRepository
    secret: str

    def execute(
        self,
        jeton_session: str,
        montant_demande: int,
        objet_credit: str,
        duree_mois: int,
        produit_id: str | None = None,
        revenu_mensuel_declare: int | None = None,
        charges_mensuelles: int | None = None,
    ) -> ResultatDemandeSocietaire:
        societaire_id = verifier_jeton(self.secret, jeton_session)
        if societaire_id is None:
            raise IdentiteSocietaireInvalide("Session expirée, recommencez depuis l'accueil.")

        societaire = self.core_sim_reader.charger_societaire(societaire_id)
        if societaire is None:
            raise SocietaireIntrouvable(societaire_id)

        # Le sociétaire ne choisit plus de produit (étape retirée du parcours, "Pour quoi
        # faire ?" seul suffit) : le produit se déduit de son segment CORE-SIM, seule
        # correspondance produit/segment réellement établie dans le catalogue à ce jour.
        if produit_id is None:
            produit_id = self._resoudre_produit_par_segment(societaire.segment)

        # Le sociétaire peut estimer ces deux montants comme l'agent le fait déjà
        # (ActualisationSituation, RefreshFields.tsx côté agent) : sans ça, une demande venue
        # du portail n'a jamais de revenu déclaré et le plafond par capacité de remboursement
        # (montant_maximal_supportable) ne s'applique jamais aux demandes clients.
        actualisation = (
            ActualisationSituation(
                revenu_mensuel_declare=revenu_mensuel_declare,
                charges_mensuelles=charges_mensuelles,
            )
            if revenu_mensuel_declare is not None or charges_mensuelles is not None
            else None
        )

        demande = DemandeScoring(
            societaire_id=societaire_id,
            produit_id=produit_id,
            montant_demande=montant_demande,
            duree_demandee_mois=duree_mois,
            objet_credit=objet_credit,
            groupe_id=societaire.groupe_id,
            actualisation=actualisation,
        )
        decision = self.scorer_demande.preview(
            demande,
            raw_input={
                "montant_demande": montant_demande,
                "objet_credit": objet_credit,
                "duree_demandee_mois": duree_mois,
                "canal": "portail_societaire",
            },
            agent_id=AGENT_ID_PORTAIL,
            agent_nom=AGENT_NOM_PORTAIL,
            agent_agence_id=None,
        )

        configuration = self.grille_repository.lire_active()
        pre_verification = calculer_pre_verification(
            decision.tranche,
            Montant(valeur=montant_demande),
            decision.montant_recommande,
            objet_credit,
            decision.conditions_reexamen,
            configuration.classification_objets,
        )

        # Un sociétaire déjà suivi par un agent voit sa demande directement affectée à cet agent
        # habituel, sans passer par la file du superviseur (celui-ci ne garde que les nouveaux
        # sociétaires, sans historique).
        agent_habituel_id = self.decision_repository.dernier_agent_reel(societaire_id)

        demande_a_creer = DemandeSocietaireACreer(
            demande_id=str(uuid.uuid4()),
            societaire_id=societaire_id,
            agence_id=societaire.agence,
            montant_demande=montant_demande,
            objet_credit=objet_credit,
            duree_mois=duree_mois,
            produit_id=produit_id,
            resultat=decision,
            assigne_a_agent_id=agent_habituel_id,
        )
        demande_enregistree = self.demande_societaire_repository.enregistrer(demande_a_creer)
        self.notification_sender.notifier(demande_enregistree)

        return ResultatDemandeSocietaire(
            demande_id=demande_enregistree.demande_id, pre_verification=pre_verification
        )

    def _resoudre_produit_par_segment(self, segment: str) -> str:
        produits = [p for p in self.core_sim_reader.charger_produits() if p.segment == segment]
        if len(produits) != 1:
            raise ProduitIntrouvable(
                f"Aucune correspondance produit/segment univoque pour le segment "
                f"'{segment}' ({len(produits)} produit(s) trouvé(s))."
            )
        return produits[0].produit_id
