from solida.domain.rules.progressif_plafond import ParametresProgressif
from solida.domain.rules.progressif_trajectoire import calculer_trajectoire
from solida.domain.values.montant import Montant
from solida.domain.values.probabilite import ProbabiliteDefaut

PARAMETRES = ParametresProgressif(
    coefficient_progression=1.5,
    montant_plancher=Montant(50_000),
    plafond_primo_emprunteur=Montant(150_000),
    plafonds_produits={},
)
PLAFOND_PRODUIT = Montant(3_000_000)


def test_la_trajectoire_applique_par_defaut_le_coefficient_et_la_modulation_sur_un_seul_cycle() -> (
    None
):
    trajectoire = calculer_trajectoire(
        Montant(165_600), ProbabiliteDefaut(0.19), PARAMETRES, PLAFOND_PRODUIT
    )

    assert [p.cycle for p in trajectoire] == [1]
    assert trajectoire[0].plafond_accessible.valeur == 228_528


def test_la_trajectoire_est_bornee_par_le_plafond_produit() -> None:
    trajectoire = calculer_trajectoire(
        Montant(2_500_000), ProbabiliteDefaut(0.1), PARAMETRES, PLAFOND_PRODUIT
    )

    assert trajectoire[0].plafond_accessible.valeur == 3_000_000


def test_la_trajectoire_peut_projeter_plusieurs_cycles_si_explicitement_demande() -> None:
    trajectoire = calculer_trajectoire(
        Montant(165_600), ProbabiliteDefaut(0.19), PARAMETRES, PLAFOND_PRODUIT, nb_cycles=3
    )

    assert [p.cycle for p in trajectoire] == [1, 2, 3]
    assert [p.plafond_accessible.valeur for p in trajectoire] == [228_528, 315_369, 435_209]
