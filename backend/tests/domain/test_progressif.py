from solida.domain.rules.progressif import (
    ParametresProgressif,
    ParametresReexamen,
    SituationReexamen,
    calculer_plafond,
    calculer_trajectoire,
    lister_conditions_reexamen,
)
from solida.domain.values.montant import Montant
from solida.domain.values.probabilite import ProbabiliteDefaut

PARAMETRES = ParametresProgressif(
    coefficient_progression=1.5,
    montant_plancher=Montant(50_000),
    plafond_produit=Montant(3_000_000),
    plafond_primo_emprunteur=Montant(150_000),
)


def test_un_primo_emprunteur_est_plafonne_par_le_plafond_primo_emprunteur() -> None:
    plafond = calculer_plafond(None, Montant(200_000), ProbabiliteDefaut(0.1), PARAMETRES)

    assert plafond == Montant(150_000)


def test_le_plancher_prevaut_meme_pour_un_primo_emprunteur_qui_demande_moins() -> None:
    plafond = calculer_plafond(None, Montant(30_000), ProbabiliteDefaut(0.1), PARAMETRES)

    assert plafond == Montant(50_000)


def test_le_plafond_reprend_exactement_le_calcul_du_prototype_de_reference() -> None:
    plafond = calculer_plafond(
        Montant(120_000), Montant(250_000), ProbabiliteDefaut(0.19), PARAMETRES
    )

    assert plafond == Montant(165_600)


def test_la_modulation_est_plafonnee_a_1_2_pour_un_risque_tres_faible() -> None:
    plafond = calculer_plafond(
        Montant(100_000), Montant(1_000_000), ProbabiliteDefaut(0.01), PARAMETRES
    )

    assert plafond == Montant(180_000)


def test_la_modulation_est_plancher_a_0_4_pour_un_risque_eleve() -> None:
    plafond = calculer_plafond(
        Montant(100_000), Montant(1_000_000), ProbabiliteDefaut(0.6), PARAMETRES
    )

    assert plafond == Montant(60_000)


def test_le_plafond_produit_borne_le_resultat() -> None:
    plafond = calculer_plafond(
        Montant(5_000_000), Montant(10_000_000), ProbabiliteDefaut(0.1), PARAMETRES
    )

    assert plafond == Montant(3_000_000)


def test_le_montant_demande_borne_le_resultat() -> None:
    plafond = calculer_plafond(
        Montant(200_000), Montant(100_000), ProbabiliteDefaut(0.1), PARAMETRES
    )

    assert plafond == Montant(100_000)


def test_la_trajectoire_applique_le_coefficient_de_progression_sur_trois_cycles() -> None:
    trajectoire = calculer_trajectoire(Montant(165_600), PARAMETRES)

    assert [p.cycle for p in trajectoire] == [1, 2, 3]
    assert [p.plafond_accessible.valeur for p in trajectoire] == [248_400, 372_600, 558_900]


def test_la_trajectoire_est_bornee_par_le_plafond_produit() -> None:
    trajectoire = calculer_trajectoire(Montant(2_500_000), PARAMETRES)

    assert [p.plafond_accessible.valeur for p in trajectoire] == [3_000_000, 3_000_000, 3_000_000]


SITUATION_PARAMETRES = ParametresReexamen()


def test_un_dossier_sans_aucun_levier_bloquant_le_dit_explicitement() -> None:
    situation = SituationReexamen(
        regularite_epargne=0.9,
        ratio_garantie=0.6,
        endettement=0.3,
        tendance_epargne_baissiere=False,
        caution_deja_appelee=False,
        montant_demande=Montant(250_000),
    )

    conditions = lister_conditions_reexamen(situation, SITUATION_PARAMETRES)

    assert conditions == [
        "Aucun levier bloquant : le dossier peut etre reexamine des le prochain cycle."
    ]


def test_un_dossier_avec_tous_les_leviers_actifs_liste_les_cinq_conditions() -> None:
    situation = SituationReexamen(
        regularite_epargne=0.42,
        ratio_garantie=0.31,
        endettement=0.58,
        tendance_epargne_baissiere=True,
        caution_deja_appelee=True,
        montant_demande=Montant(250_000),
    )

    conditions = lister_conditions_reexamen(situation, SITUATION_PARAMETRES)

    assert len(conditions) == 5
    assert "depot" in conditions[0]
    assert "125 000 FCFA" in conditions[1]
    assert "endettement" in conditions[2] or "remboursement" in conditions[2]
    assert "epargne" in conditions[3]
    assert "caution" in conditions[4]
