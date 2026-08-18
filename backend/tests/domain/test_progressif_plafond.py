from solida.domain.rules.progressif_plafond import ParametresProgressif, calculer_plafond
from solida.domain.values.montant import Montant
from solida.domain.values.probabilite import ProbabiliteDefaut

PARAMETRES = ParametresProgressif(
    coefficient_progression=1.5,
    montant_plancher=Montant(50_000),
    plafond_primo_emprunteur=Montant(150_000),
    plafonds_produits={},
)
PLAFOND_PRODUIT = Montant(3_000_000)


def test_un_primo_emprunteur_est_plafonne_par_le_plafond_primo_emprunteur() -> None:
    plafond = calculer_plafond(
        None, Montant(200_000), ProbabiliteDefaut(0.1), PARAMETRES, PLAFOND_PRODUIT
    )

    assert plafond == Montant(150_000)


def test_le_plancher_prevaut_meme_pour_un_primo_emprunteur_qui_demande_moins() -> None:
    plafond = calculer_plafond(
        None, Montant(30_000), ProbabiliteDefaut(0.1), PARAMETRES, PLAFOND_PRODUIT
    )

    assert plafond == Montant(50_000)


def test_le_plafond_reprend_exactement_le_calcul_du_prototype_de_reference() -> None:
    plafond = calculer_plafond(
        Montant(120_000), Montant(250_000), ProbabiliteDefaut(0.19), PARAMETRES, PLAFOND_PRODUIT
    )

    assert plafond == Montant(165_600)


def test_la_modulation_est_plafonnee_a_1_2_pour_un_risque_tres_faible() -> None:
    plafond = calculer_plafond(
        Montant(100_000), Montant(1_000_000), ProbabiliteDefaut(0.01), PARAMETRES, PLAFOND_PRODUIT
    )

    assert plafond == Montant(180_000)


def test_la_modulation_est_plancher_a_0_4_pour_un_risque_eleve() -> None:
    plafond = calculer_plafond(
        Montant(100_000), Montant(1_000_000), ProbabiliteDefaut(0.6), PARAMETRES, PLAFOND_PRODUIT
    )

    assert plafond == Montant(60_000)


def test_le_plafond_produit_borne_le_resultat() -> None:
    plafond = calculer_plafond(
        Montant(5_000_000), Montant(10_000_000), ProbabiliteDefaut(0.1), PARAMETRES, PLAFOND_PRODUIT
    )

    assert plafond == Montant(3_000_000)


def test_le_montant_demande_borne_le_resultat() -> None:
    plafond = calculer_plafond(
        Montant(200_000), Montant(100_000), ProbabiliteDefaut(0.1), PARAMETRES, PLAFOND_PRODUIT
    )

    assert plafond == Montant(100_000)
