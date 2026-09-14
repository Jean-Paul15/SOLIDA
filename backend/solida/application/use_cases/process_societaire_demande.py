import uuid
from dataclasses import dataclass

from solida.application.use_cases.scorer_demande import ScorerDemande
from solida.domain.errors import IdentiteSocietaireInvalide, SocietaireIntrouvable
from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.ports.demande_societaire import DemandeSocietaireRepository
from solida.domain.ports.notification_sender import NotificationSender
from solida.domain.rules.jeton_societaire import verifier_jeton
from solida.domain.rules.pre_verification import PreVerification, calculer_pre_verification
from solida.domain.values.demande import DemandeScoring
from solida.domain.values.demande_societaire import DemandeSocietaireACreer
from solida.domain.values.montant import Montant

AGENT_ID_PORTAIL = "portail-societaire"
AGENT_NOM_PORTAIL = "Portail sociétaire"


@dataclass(frozen=True)
class ResultatDemandeSocietaire:
    demande_id: str
    pre_verification: PreVerification


def _produit_id_depuis_segment(segment: str) -> str:
    return f"prod-{segment.replace('_', '-')}"


@dataclass(frozen=True)
class ProcessSocietaireDemande:
    core_sim_reader: CoreSimReader
    scorer_demande: ScorerDemande
    demande_societaire_repository: DemandeSocietaireRepository
    notification_sender: NotificationSender
    secret: str

    def execute(
        self,
        jeton_session: str,
        montant_demande: int,
        objet_credit: str,
        duree_mois: int,
    ) -> ResultatDemandeSocietaire:
        societaire_id = verifier_jeton(self.secret, jeton_session)
        if societaire_id is None:
            raise IdentiteSocietaireInvalide("Session expirée, recommencez depuis l'accueil.")

        societaire = self.core_sim_reader.charger_societaire(societaire_id)
        if societaire is None:
            raise SocietaireIntrouvable(societaire_id)

        produit_id = _produit_id_depuis_segment(societaire.segment)
        demande = DemandeScoring(
            societaire_id=societaire_id,
            produit_id=produit_id,
            montant_demande=montant_demande,
            duree_demandee_mois=duree_mois,
            objet_credit=objet_credit,
            groupe_id=societaire.groupe_id,
            actualisation=None,
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

        pre_verification = calculer_pre_verification(
            decision.tranche,
            Montant(valeur=montant_demande),
            decision.montant_recommande,
            objet_credit,
            decision.conditions_reexamen,
        )

        demande_a_creer = DemandeSocietaireACreer(
            demande_id=str(uuid.uuid4()),
            societaire_id=societaire_id,
            agence_id=societaire.agence,
            montant_demande=montant_demande,
            objet_credit=objet_credit,
            duree_mois=duree_mois,
            produit_id=produit_id,
            resultat=decision,
        )
        demande_enregistree = self.demande_societaire_repository.enregistrer(demande_a_creer)
        self.notification_sender.notifier(demande_enregistree)

        return ResultatDemandeSocietaire(
            demande_id=demande_enregistree.demande_id, pre_verification=pre_verification
        )
