from solida.domain.entities.compte_epargne import CompteEpargne
from solida.domain.entities.groupe import GroupeCaution
from solida.domain.values.dossier import CreditResume, MembreGroupeAffiche, SyntheseGroupe

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


def _ratio_epargne_revenu(compte: CompteEpargne | None, revenu: int | None) -> float:
    if compte is None or not revenu:
        return 0.0
    return min(compte.solde_moyen_6m / revenu, 5.0)
