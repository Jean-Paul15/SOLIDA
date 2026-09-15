from dataclasses import dataclass, replace
from datetime import UTC, datetime

import pytest

from solida.application.use_cases.gerer_grille import ModifierGrille
from solida.domain.errors import ScorecardImmuable
from solida.domain.rules.grille import ParametresGrille
from solida.domain.rules.progressif_plafond import ParametresProgressif
from solida.domain.rules.scorecard import ParametresScorecard
from solida.domain.values.grille import ConfigurationGrille
from solida.domain.values.montant import Montant

PARAMETRES_SCORECARD = ParametresScorecard(
    pdo=20, score_reference=600, odds_reference=50, score_min=300, score_max=850
)


def _configuration(**overrides: object) -> ConfigurationGrille:
    values: dict[str, object] = {
        "version_grille": "v1",
        "grille": ParametresGrille(marge=0.1, lgd=0.5),
        "progressif": ParametresProgressif(
            coefficient_progression=1.5,
            montant_plancher=Montant(50000),
            plafond_primo_emprunteur=Montant(150000),
            plafonds_produits={},
        ),
        "scorecard": PARAMETRES_SCORECARD,
        "auteur": "test",
        "date_activation": datetime.now(UTC),
        "active": True,
    }
    values.update(overrides)
    return ConfigurationGrille(**values)  # type: ignore[arg-type]


@dataclass
class _FakeGrilleRepository:
    active: ConfigurationGrille
    enregistree: ConfigurationGrille | None = None

    def lire_active(self) -> ConfigurationGrille:
        return self.active

    def enregistrer_nouvelle_version(
        self, configuration: ConfigurationGrille
    ) -> ConfigurationGrille:
        self.enregistree = configuration
        return configuration


def test_modifier_grille_reporte_classification_et_objets_implicites_de_la_grille_active() -> (
    None
):
    active = _configuration(
        classification_objets={"stock": "divisible"},
        objets_implicites_produits={"PROD-AGRICOLE": "intrants_agricoles"},
    )
    depot = _FakeGrilleRepository(active=active)
    use_case = ModifierGrille(grille_repository=depot)
    # Construite comme le ferait le routeur HTTP : ces deux champs à leur valeur par défaut
    # ({}), puisqu'aucun schéma HTTP ne les expose.
    nouvelle = _configuration(version_grille="v2", grille=ParametresGrille(marge=0.2, lgd=0.6))

    use_case.execute(nouvelle)

    assert depot.enregistree is not None
    assert depot.enregistree.classification_objets == {"stock": "divisible"}
    assert depot.enregistree.objets_implicites_produits == {
        "PROD-AGRICOLE": "intrants_agricoles"
    }


def test_modifier_grille_refuse_un_changement_de_scorecard() -> None:
    active = _configuration()
    depot = _FakeGrilleRepository(active=active)
    use_case = ModifierGrille(grille_repository=depot)
    nouvelle = replace(
        active,
        version_grille="v2",
        scorecard=replace(PARAMETRES_SCORECARD, pdo=25),
    )

    with pytest.raises(ScorecardImmuable):
        use_case.execute(nouvelle)
