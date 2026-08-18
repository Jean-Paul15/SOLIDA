from solida.domain.rules.progressif_reexamen import (
    ParametresReexamen,
    SituationReexamen,
    lister_conditions_reexamen,
)
from solida.domain.values.montant import Montant

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
        "Aucun levier bloquant : le dossier peut être réexaminé dès le prochain cycle."
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
    assert "dépôt" in conditions[0]
    assert "125 000 FCFA" in conditions[1]
    assert "endettement" in conditions[2] or "remboursement" in conditions[2]
    assert "épargne" in conditions[3]
    assert "caution" in conditions[4]
