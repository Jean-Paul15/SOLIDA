from solida.domain.rules.pre_verification import (
    DIVISIBLE,
    INDIVISIBLE,
    ISSUE_DUREE_OU_ATTENTE,
    ISSUE_MONTANT_REDUIT,
    ISSUE_PAS_MAINTENANT,
    ISSUE_PEUT_AVANCER,
    ISSUE_REVUE_OBLIGATOIRE,
    NON_CLASSE,
    OBJET_AUTRE,
    calculer_pre_verification,
    classe_objet,
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
        {},
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
        {"stock": DIVISIBLE},
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
        {"equipement": INDIVISIBLE},
    )
    assert resultat.issue == ISSUE_DUREE_OU_ATTENTE
    assert resultat.montant_propose is None


def test_table_de_classification_vide_ne_reduit_jamais_le_montant() -> None:
    """Comportement par défaut tant qu'aucune table métier réelle n'est fournie."""
    resultat = calculer_pre_verification(
        TrancheDecision.ACCORD_SOUS_CONDITION,
        Montant(valeur=300_000),
        Montant(valeur=150_000),
        "stock",
        [],
        {},
    )
    assert resultat.issue == ISSUE_DUREE_OU_ATTENTE
    assert resultat.montant_propose is None


def test_classe_objet_renvoie_non_classe_si_absent_de_la_table() -> None:
    assert classe_objet("objet_inconnu", {"stock": DIVISIBLE}) == NON_CLASSE


def test_objet_autre_est_toujours_une_revue_obligatoire_meme_en_accord() -> None:
    """Un objet non classifié route vers l'examen humain quelle que soit la tranche : le
    modèle recommanderait un accord franc ici, mais l'objet prime."""
    resultat = calculer_pre_verification(
        TrancheDecision.ACCORD,
        Montant(valeur=100_000),
        Montant(valeur=100_000),
        OBJET_AUTRE,
        [],
        {},
    )
    assert resultat.issue == ISSUE_REVUE_OBLIGATOIRE
    assert resultat.montant_propose is None


def test_objet_autre_prime_meme_sur_un_refus() -> None:
    resultat = calculer_pre_verification(
        TrancheDecision.REFUS,
        Montant(valeur=100_000),
        Montant(valeur=0),
        OBJET_AUTRE,
        ["Effectuer un dépôt chaque mois pendant 3 mois."],
        {},
    )
    assert resultat.issue == ISSUE_REVUE_OBLIGATOIRE


def test_refus_reprend_les_conditions_de_reexamen_dans_le_message() -> None:
    resultat = calculer_pre_verification(
        TrancheDecision.REFUS,
        Montant(valeur=100_000),
        Montant(valeur=0),
        "fonds_roulement",
        ["Effectuer un dépôt chaque mois pendant 3 mois."],
        {},
    )
    assert resultat.issue == ISSUE_PAS_MAINTENANT
    assert "Effectuer un dépôt chaque mois pendant 3 mois." in resultat.message
