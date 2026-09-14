from datetime import date

from solida_modelisation.features_groupe import (
    AppartenanceGie,
    CautionGroupe,
    CreditGroupeAnterieur,
    EcheanceGroupe,
    calculer_features_groupe,
    taille_groupe_a_date,
)


def _appartenances(nb_actifs: int) -> list[AppartenanceGie]:
    return [
        AppartenanceGie(f"SOC-{i}", date(2020, 1, 1), None) for i in range(nb_actifs)
    ]


def test_membre_sorti_avant_la_reference_non_compte() -> None:
    appartenances = [
        *_appartenances(5),
        AppartenanceGie("SOC-SORTANT", date(2020, 1, 1), date(2024, 1, 1)),
    ]
    assert taille_groupe_a_date(appartenances, date(2024, 6, 1)) == 5


def test_membre_sorti_apres_la_reference_compte() -> None:
    appartenances = [
        *_appartenances(5),
        AppartenanceGie("SOC-SORTANT", date(2020, 1, 1), date(2024, 12, 1)),
    ]
    assert taille_groupe_a_date(appartenances, date(2024, 6, 1)) == 6


def test_groupe_sous_le_seuil_renvoie_des_features_manquantes() -> None:
    resultat = calculer_features_groupe(
        date_reference=date(2025, 1, 1),
        date_creation_groupe=date(2020, 1, 1),
        appartenances=_appartenances(4),
        credits_anterieurs=[],
        echeances_groupe=[],
        cautions_anterieures=[],
    )
    assert resultat.taille_groupe == 4
    assert resultat.anciennete_groupe_mois is None
    assert resultat.nb_credits_groupe_anterieurs is None
    assert resultat.nb_incidents_groupe_anterieurs is None
    assert resultat.max_jours_retard_groupe_6m is None
    assert resultat.nb_cautions_appelees_anterieures is None


def test_echeance_de_groupe_posterieure_a_la_reference_sans_effet() -> None:
    credits = [CreditGroupeAnterieur("CRD-1", date(2024, 1, 1), date(2024, 4, 1))]
    echeances = [
        EcheanceGroupe("CRD-1", date(2024, 2, 1), 0.0),
        # Paiement en retard mais connu seulement après la référence : ignoré.
        EcheanceGroupe("CRD-1", date(2025, 6, 1), 45.0),
    ]
    resultat = calculer_features_groupe(
        date_reference=date(2025, 1, 1),
        date_creation_groupe=date(2020, 1, 1),
        appartenances=_appartenances(5),
        credits_anterieurs=credits,
        echeances_groupe=echeances,
        cautions_anterieures=[],
    )
    assert resultat.nb_incidents_groupe_anterieurs == 0


def test_incident_de_groupe_observable_avant_la_reference() -> None:
    credits = [CreditGroupeAnterieur("CRD-1", date(2024, 1, 1), date(2024, 4, 1))]
    echeances = [EcheanceGroupe("CRD-1", date(2024, 3, 1), 35.0)]
    resultat = calculer_features_groupe(
        date_reference=date(2025, 1, 1),
        date_creation_groupe=date(2020, 1, 1),
        appartenances=_appartenances(5),
        credits_anterieurs=credits,
        echeances_groupe=echeances,
        cautions_anterieures=[],
    )
    assert resultat.nb_incidents_groupe_anterieurs == 1
    assert resultat.nb_credits_groupe_anterieurs == 1


def test_fenetre_6_mois_exclut_un_retard_plus_ancien() -> None:
    credits = [CreditGroupeAnterieur("CRD-1", date(2023, 1, 1), date(2023, 4, 1))]
    echeances = [EcheanceGroupe("CRD-1", date(2024, 1, 1), 40.0)]
    resultat = calculer_features_groupe(
        date_reference=date(2025, 1, 1),
        date_creation_groupe=date(2020, 1, 1),
        appartenances=_appartenances(5),
        credits_anterieurs=credits,
        echeances_groupe=echeances,
        cautions_anterieures=[],
    )
    assert resultat.max_jours_retard_groupe_6m is None
    assert resultat.nb_incidents_groupe_anterieurs == 1


def test_caution_appelee_sur_credit_non_clos_ignoree() -> None:
    credits = [CreditGroupeAnterieur("CRD-1", date(2024, 6, 1), None)]
    cautions = [CautionGroupe("CRD-1", True)]
    resultat = calculer_features_groupe(
        date_reference=date(2025, 1, 1),
        date_creation_groupe=date(2020, 1, 1),
        appartenances=_appartenances(5),
        credits_anterieurs=credits,
        echeances_groupe=[],
        cautions_anterieures=cautions,
    )
    assert resultat.nb_cautions_appelees_anterieures == 0


def test_caution_appelee_sur_credit_clos_comptee() -> None:
    credits = [CreditGroupeAnterieur("CRD-1", date(2024, 1, 1), date(2024, 4, 1))]
    cautions = [CautionGroupe("CRD-1", True)]
    resultat = calculer_features_groupe(
        date_reference=date(2025, 1, 1),
        date_creation_groupe=date(2020, 1, 1),
        appartenances=_appartenances(5),
        credits_anterieurs=credits,
        echeances_groupe=[],
        cautions_anterieures=cautions,
    )
    assert resultat.nb_cautions_appelees_anterieures == 1


def test_credit_futur_non_compte_comme_anterieur() -> None:
    credits = [CreditGroupeAnterieur("CRD-FUTUR", date(2025, 6, 1), None)]
    resultat = calculer_features_groupe(
        date_reference=date(2025, 1, 1),
        date_creation_groupe=date(2020, 1, 1),
        appartenances=_appartenances(5),
        credits_anterieurs=credits,
        echeances_groupe=[],
        cautions_anterieures=[],
    )
    assert resultat.nb_credits_groupe_anterieurs == 0
