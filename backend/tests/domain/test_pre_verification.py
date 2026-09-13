from solida.domain.rules.pre_verification import (
    ISSUE_DUREE_OU_ATTENTE,
    ISSUE_MONTANT_REDUIT,
    ISSUE_PAS_MAINTENANT,
    ISSUE_PEUT_AVANCER,
    calculer_pre_verification,
)
from solida.domain.values.montant import Montant
from solida.domain.values.tranche import TrancheDecision


def test_accord_avec_montant_couvert_donne_peut_avancer() -> None:
    resultat = calculer_pre_verification(
        TrancheDecision.ACCORD,
        Montant(valeur=100_000),
        Montant(valeur=100_000),
        "fonds_roulement",
        [],
    )
    assert resultat.issue == ISSUE_PEUT_AVANCER
    assert resultat.montant_propose is None
    assert "score" not in resultat.message.lower()
    assert "probabilité" not in resultat.message.lower()


def test_montant_reduit_sur_objet_divisible_propose_le_montant_recommande() -> None:
    resultat = calculer_pre_verification(
        TrancheDecision.ACCORD_SOUS_CONDITION,
        Montant(valeur=300_000),
        Montant(valeur=150_000),
        "stock",
        [],
    )
    assert resultat.issue == ISSUE_MONTANT_REDUIT
    assert resultat.montant_propose == 150_000
    assert "150 000" in resultat.message


def test_jamais_de_montant_reduit_sur_objet_indivisible() -> None:
    resultat = calculer_pre_verification(
        TrancheDecision.ACCORD_SOUS_CONDITION,
        Montant(valeur=300_000),
        Montant(valeur=150_000),
        "equipement",
        [],
    )
    assert resultat.issue == ISSUE_DUREE_OU_ATTENTE
    assert resultat.montant_propose is None


def test_objet_hors_table_1_7_traite_comme_mixte_donc_pas_de_montant_reduit() -> None:
    resultat = calculer_pre_verification(
        TrancheDecision.ACCORD_SOUS_CONDITION,
        Montant(valeur=300_000),
        Montant(valeur=150_000),
        "urgence_sante",
        [],
    )
    assert resultat.issue == ISSUE_DUREE_OU_ATTENTE


def test_comite_de_credit_est_traite_comme_duree_ou_attente() -> None:
    resultat = calculer_pre_verification(
        TrancheDecision.COMITE_DE_CREDIT,
        Montant(valeur=100_000),
        Montant(valeur=100_000),
        "fonds_roulement",
        [],
    )
    assert resultat.issue == ISSUE_DUREE_OU_ATTENTE


def test_refus_reprend_les_conditions_de_reexamen_dans_le_message() -> None:
    resultat = calculer_pre_verification(
        TrancheDecision.REFUS,
        Montant(valeur=100_000),
        Montant(valeur=0),
        "fonds_roulement",
        ["Effectuer un dépôt chaque mois pendant 3 mois."],
    )
    assert resultat.issue == ISSUE_PAS_MAINTENANT
    assert "Effectuer un dépôt chaque mois pendant 3 mois." in resultat.message
