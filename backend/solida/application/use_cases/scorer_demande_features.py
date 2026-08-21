from dataclasses import replace

from solida.domain.rules.echeance import (
    TAUX_MENSUEL_DEMONSTRATION,
    calculer_echeance_mensuelle,
    calculer_taux_endettement,
)
from solida.domain.values.demande import DemandeScoring
from solida.domain.values.features import FeaturesIndividuelles


def _revenu_effectif(demande: DemandeScoring, revenu_declare: int | None) -> int:
    if demande.actualisation and demande.actualisation.revenu_mensuel_declare is not None:
        return demande.actualisation.revenu_mensuel_declare
    return revenu_declare or 0


def _actualiser_features(
    features: FeaturesIndividuelles, demande: DemandeScoring, revenu_effectif: int
) -> FeaturesIndividuelles:
    """Remplace les ratios qui dépendent du montant/de la durée demandés, ou d'un revenu
    actualisé par l'agent : `FeatureStore` ne connaît que le profil du sociétaire, pas la
    demande en cours (voir `FeatureStoreCoreSim`).
    """
    charges = demande.actualisation.charges_mensuelles if demande.actualisation else None
    mensualite = calculer_echeance_mensuelle(
        demande.montant_demande, demande.duree_demandee_mois, TAUX_MENSUEL_DEMONSTRATION
    )
    ratio_endettement = calculer_taux_endettement(charges or 0, revenu_effectif, mensualite)
    ratio_epargne_montant = min(features.solde_epargne_moyen_6m / demande.montant_demande, 3.0)
    ratio_epargne_revenu = (
        min(features.solde_epargne_moyen_6m / revenu_effectif, 5.0) if revenu_effectif > 0 else 0.0
    )
    nb_personnes_a_charge = (
        demande.actualisation.nb_personnes_a_charge
        if demande.actualisation and demande.actualisation.nb_personnes_a_charge is not None
        else features.nb_personnes_a_charge
    )
    return replace(
        features,
        ratio_endettement=ratio_endettement,
        ratio_epargne_montant=ratio_epargne_montant,
        ratio_epargne_revenu=ratio_epargne_revenu,
        nb_personnes_a_charge=nb_personnes_a_charge,
    )


def _features_to_dict(individuelles: FeaturesIndividuelles, en_groupe: bool) -> dict[str, float]:
    """Ne garde que les champs numériques : `predire()`/`contributions()` attendent des
    variables du modèle, pas les champs texte (`segment`, `tendance_epargne_12m`), et une
    valeur `None` (primo-emprunteur) est omise plutôt que remplacée par un zéro trompeur.
    """
    valeurs: dict[str, float | None] = {
        "anciennete_societaire_mois": individuelles.anciennete_societaire_mois,
        "solde_epargne_moyen_6m": individuelles.solde_epargne_moyen_6m,
        "nb_mois_avec_depot_12m": individuelles.nb_mois_avec_depot_12m,
        "volatilite_epargne": individuelles.volatilite_epargne,
        "ratio_epargne_revenu": individuelles.ratio_epargne_revenu,
        "ratio_epargne_montant": individuelles.ratio_epargne_montant,
        "anciennete_epargne_mois": individuelles.anciennete_epargne_mois,
        "ratio_endettement": individuelles.ratio_endettement,
        "nb_credits_anterieurs": individuelles.nb_credits_anterieurs,
        "nb_incidents_anterieurs": individuelles.nb_incidents_anterieurs,
        "max_jours_retard_historique": individuelles.max_jours_retard_historique,
        "montant_max_rembourse": individuelles.montant_max_rembourse,
        "numero_cycle": individuelles.numero_cycle,
        "parts_sociales_montant": individuelles.parts_sociales_montant,
        "nb_personnes_a_charge": individuelles.nb_personnes_a_charge,
        "en_groupe": 1.0 if en_groupe else 0.0,
    }
    return {code: valeur for code, valeur in valeurs.items() if valeur is not None}
