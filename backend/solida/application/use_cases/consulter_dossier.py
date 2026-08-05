from dataclasses import dataclass
from datetime import date, timedelta

from solida.domain.entities.compte_epargne import CompteEpargne
from solida.domain.entities.groupe import GroupeCaution
from solida.domain.ports.core_sim import LecteurCoreSim
from solida.domain.rules.epargne import tendance_depuis_croissance
from solida.domain.values.dossier import (
    ActiviteEconomique,
    CreditResume,
    DossierSocietaire,
    IdentiteSocietaire,
    MembreGroupeAffiche,
    MouvementEpargneAffiche,
    SyntheseEpargne,
    SyntheseGroupe,
)

DUREE_HISTORIQUE_MOUVEMENTS = timedelta(days=365)

STATUT_SOCIETAIRE_PAR_DEFAUT = "actif"
"""Le générateur ne modélise ni churn ni radiation, voir `LecteurCoreSimPostgres`."""

# Le générateur ne produit pas de secteur d'activité distinct du segment (produit souscrit) :
# correspondance provisoire, voir docs/backend/03-decisions-provisoires-a-revoir.md.
SECTEUR_PAR_SEGMENT = {
    "agricole": "Agriculture",
    "salarie": "Salariat",
    "individuel": "Commerce et services",
    "jeune": "Activité en démarrage",
    "femme_gie": "Commerce (groupement)",
}


def _secteur(segment: str) -> str:
    return SECTEUR_PAR_SEGMENT.get(segment, "Non renseigné")


def _groupe_affiche(groupe: GroupeCaution | None) -> SyntheseGroupe | None:
    if groupe is None:
        return None
    return SyntheseGroupe(
        groupe_id=groupe.groupe_id,
        nom_groupe=groupe.nom_groupe,
        taille_actuelle=groupe.taille_actuelle,
        date_creation=groupe.date_creation,
        taux_remboursement_groupe=groupe.taux_remboursement_groupe,
        nb_cycles_completes=groupe.nb_cycles_completes,
        nb_sorties_12m=groupe.nb_sorties_12m,
        statut=groupe.statut,
        membres=[
            MembreGroupeAffiche(
                societaire_id=m.societaire_id,
                nom_complet=m.nom_complet,
                role=m.role,
                anciennete_mois=m.anciennete_mois,
                statut_credit=m.statut_credit,
                caution_appelee=m.caution_appelee,
            )
            for m in groupe.membres
        ],
    )


def _alertes(credits: list[CreditResume], groupe: SyntheseGroupe | None) -> list[str]:
    alertes = []
    if any(c.statut == "en_souffrance" for c in credits):
        alertes.append("Un crédit en souffrance figure dans l'historique.")
    if groupe is not None:
        if groupe.statut == "en_difficulte":
            alertes.append("Le groupe de caution est en difficulté.")
        if any(m.caution_appelee for m in groupe.membres):
            alertes.append("Une caution a déjà été appelée dans le groupe.")
    return alertes


@dataclass(frozen=True)
class ConsulterDossier:
    lecteur: LecteurCoreSim

    def executer(self, societaire_id: str) -> DossierSocietaire | None:
        societaire = self.lecteur.charger_societaire(societaire_id)
        if societaire is None:
            return None

        credits = self.lecteur.charger_historique_credit(societaire_id)
        compte = self.lecteur.charger_compte_epargne(societaire_id)
        groupe = _groupe_affiche(self.lecteur.charger_groupe(societaire_id))
        mouvements = self.lecteur.charger_mouvements_epargne(
            societaire_id, depuis=date.today() - DUREE_HISTORIQUE_MOUVEMENTS
        )

        historique = [
            CreditResume(
                credit_id=c.credit_id,
                date_deblocage=c.date_deblocage,
                montant_octroye=c.montant_octroye,
                duree_mois=c.duree_mois,
                numero_cycle=c.numero_cycle,
                statut=c.statut,
                capital_restant_du=c.capital_restant_du,
                max_jours_retard=c.jours_retard_max or 0,
            )
            for c in credits
        ]

        return DossierSocietaire(
            identite=IdentiteSocietaire(
                societaire_id=societaire.societaire_id,
                numero_membre=societaire.numero_membre,
                nom_complet=societaire.nom_complet,
                segment=societaire.segment,
                agence=societaire.agence,
                date_adhesion=societaire.date_adhesion,
                anciennete_mois=societaire.anciennete_mois,
                statut=STATUT_SOCIETAIRE_PAR_DEFAUT,
                age=societaire.age,
                niveau_instruction=societaire.niveau_instruction,
            ),
            activite=ActiviteEconomique(
                secteur=_secteur(societaire.segment),
                anciennete_activite_mois=societaire.anciennete_mois,
                revenu_mensuel_declare=societaire.revenu_mensuel_declare,
                charges_mensuelles=None,
                capacite_remboursement_estimee=societaire.revenu_mensuel_declare or 0,
                nb_personnes_a_charge=societaire.nb_personnes_a_charge,
                parts_sociales_montant=societaire.parts_sociales_montant,
            ),
            epargne=SyntheseEpargne(
                solde_moyen_6m=compte.solde_moyen_6m if compte else 0,
                tendance_12m=tendance_depuis_croissance(compte.croissance_12m if compte else 0.0),
                nb_mois_avec_depot_12m=compte.nb_mois_avec_depot_12m if compte else 0,
                volatilite=compte.volatilite if compte else 0.0,
                ratio_epargne_revenu=_ratio_epargne_revenu(
                    compte, societaire.revenu_mensuel_declare
                ),
                anciennete_relation_mois=societaire.anciennete_mois,
                # CORE-SIM n'expose pas de solde mensuel absolu, seulement des agregats
                # (moyenne 6 mois, croissance 12 mois) : reconstruire une courbe de solde a
                # partir des seuls mouvements, sans point d'ancrage, serait fabrique, pas
                # mesure. On affiche donc les mouvements reels tels qu'ils sont observes.
                mouvements_recents=[
                    MouvementEpargneAffiche(
                        date_operation=m.date_operation, sens=m.sens, montant=m.montant
                    )
                    for m in mouvements
                ],
            ),
            historique_credit=historique,
            groupe=groupe,
            alertes=_alertes(historique, groupe),
        )


def _ratio_epargne_revenu(compte: CompteEpargne | None, revenu: int | None) -> float:
    if compte is None or not revenu:
        return 0.0
    return min(compte.solde_moyen_6m / revenu, 5.0)
