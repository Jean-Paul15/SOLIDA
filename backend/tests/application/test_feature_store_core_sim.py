from datetime import date

import pytest

from solida.adapters.core_sim.feature_store_core_sim import _statistiques_epargne_a_reference
from solida.domain.entities.mouvement_epargne import MouvementEpargne


def _mouvement(
    identifiant: str, date_operation: date, montant: int, type_operation: str = "depot"
) -> MouvementEpargne:
    return MouvementEpargne(
        mouvement_id=identifiant,
        compte_id="CPT-1",
        date_operation=date_operation,
        sens="depot",
        montant=montant,
        type_operation=type_operation,
    )


def test_epargne_rejouee_exclut_mois_courant_et_futur() -> None:
    mouvements = [
        _mouvement(f"MVT-{mois}", date(2024, mois, 1), 100) for mois in range(1, 9)
    ]
    mouvements.extend(
        [
            _mouvement("MVT-courant", date(2024, 9, 2), 999),
            _mouvement("MVT-futur", date(2024, 10, 1), 9_999),
        ]
    )

    solde_moyen, nb_depots, tendance, volatilite = _statistiques_epargne_a_reference(
        mouvements, date(2024, 1, 1), date(2024, 9, 13)
    )

    assert solde_moyen == 550
    assert nb_depots == 8
    assert tendance == "hausse"
    assert volatilite == pytest.approx(0.0)


def test_restitution_nantie_ne_compte_pas_comme_depot_regulier() -> None:
    mouvements = [
        _mouvement("MVT-1", date(2024, 1, 1), 100),
        _mouvement("MVT-2", date(2024, 2, 1), 100, "restitution_nantie"),
    ]

    _, nb_depots, _, _ = _statistiques_epargne_a_reference(
        mouvements, date(2024, 1, 1), date(2024, 3, 1)
    )

    assert nb_depots == 1
