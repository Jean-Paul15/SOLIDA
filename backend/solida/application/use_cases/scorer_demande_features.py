from dataclasses import replace

from solida_modelisation.finance import mensualite_actuarielle

from solida.domain.values.demande import DemandeScoring
from solida.domain.values.features import FeaturesIndividuelles, FeaturesSolidaires


def _revenu_effectif(demande: DemandeScoring, revenu_declare: int | None) -> int | None:
    if demande.actualisation and demande.actualisation.revenu_mensuel_declare is not None:
        return demande.actualisation.revenu_mensuel_declare
    return revenu_declare


def _actualiser_features(
    features: FeaturesIndividuelles,
    demande: DemandeScoring,
    revenu_effectif: int | None,
    taux_annuel_moyen: float,
) -> FeaturesIndividuelles:
    """Calcule les ratios de la demande actuelle sans ajouter de charge externe.

    Les charges externes déclarées ne sont pas injectées : elles n'existent pas dans
    l'historique synthétique utilisé à l'entraînement. La parité impose la mensualité
    du nouveau crédit seule.
    """
    mensualite = mensualite_actuarielle(
        demande.montant_demande, demande.duree_demandee_mois, taux_annuel_moyen
    )
    ratio_endettement = (
        mensualite / revenu_effectif
        if revenu_effectif is not None and revenu_effectif > 0
        else None
    )
    ratio_epargne_montant = min(
        features.solde_epargne_moyen_6m / demande.montant_demande,
        3.0,
    )
    ratio_epargne_revenu = (
        min(features.solde_epargne_moyen_6m / revenu_effectif, 5.0)
        if revenu_effectif is not None and revenu_effectif > 0
        else None
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
        revenu_mensuel_declare=revenu_effectif,
        ratio_montant_historique=(
            demande.montant_demande / features.montant_max_rembourse
            if features.montant_max_rembourse is not None
            else None
        ),
    )


def _features_to_dict(
    individuelles: FeaturesIndividuelles, demande: DemandeScoring
) -> dict[str, float | int | str | bool | None]:
    """Préserve catégories et absences : EBM les interprète nativement."""
    return {
        "anciennete_societaire_mois": individuelles.anciennete_societaire_mois,
        "nb_personnes_a_charge": individuelles.nb_personnes_a_charge,
        "zone_residence": individuelles.zone_residence,
        "parts_sociales_montant": individuelles.parts_sociales_montant,
        "revenu_mensuel_declare": individuelles.revenu_mensuel_declare,
        "ratio_endettement": individuelles.ratio_endettement,
        "duree_demandee_mois": demande.duree_demandee_mois,
        "solde_epargne_moyen_6m": individuelles.solde_epargne_moyen_6m,
        "nb_mois_avec_depot_12m": individuelles.nb_mois_avec_depot_12m,
        "tendance_epargne_12m": individuelles.tendance_epargne_12m,
        "volatilite_epargne": individuelles.volatilite_epargne,
        "ratio_epargne_revenu": individuelles.ratio_epargne_revenu,
        "anciennete_epargne_mois": individuelles.anciennete_epargne_mois,
        "ratio_epargne_montant": individuelles.ratio_epargne_montant,
        "nb_credits_anterieurs": individuelles.nb_credits_anterieurs,
        "nb_incidents_anterieurs": individuelles.nb_incidents_anterieurs,
        "max_jours_retard_historique": individuelles.max_jours_retard_historique,
        "montant_max_rembourse": individuelles.montant_max_rembourse,
        "numero_cycle": individuelles.numero_cycle,
        "ratio_montant_historique": individuelles.ratio_montant_historique,
    }


def _features_to_dict_enrichi(
    individuelles: FeaturesIndividuelles,
    solidaires: FeaturesSolidaires,
    demande: DemandeScoring,
) -> dict[str, float | int | str | bool | None]:
    """Catalogue enrichi : les 20 features SOCLE plus la couche solidaire (groupe
    emprunteur). N'est appelé que pour un crédit de groupe éligible (`cascade.py`)."""
    return {
        **_features_to_dict(individuelles, demande),
        "taille_groupe": solidaires.taille_groupe,
        "anciennete_groupe_mois": solidaires.anciennete_groupe_mois,
        "nb_credits_groupe_anterieurs": solidaires.nb_credits_groupe_anterieurs,
        "nb_incidents_groupe_anterieurs": solidaires.nb_incidents_groupe_anterieurs,
        "max_jours_retard_groupe_6m": solidaires.max_jours_retard_groupe_6m,
        "nb_cautions_appelees_anterieures": solidaires.nb_cautions_appelees_anterieures,
    }
