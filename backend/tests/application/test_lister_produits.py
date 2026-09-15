from dataclasses import dataclass, field
from datetime import UTC, datetime

from solida.application.use_cases.lister_produits import ListerProduits
from solida.domain.entities.produit_credit import ProduitCredit
from solida.domain.rules.grille import ParametresGrille
from solida.domain.rules.progressif_plafond import ParametresProgressif
from solida.domain.rules.scorecard import ParametresScorecard
from solida.domain.values.grille import ConfigurationGrille
from solida.domain.values.montant import Montant

PARAMETRES_SCORECARD = ParametresScorecard(
    pdo=20, score_reference=600, odds_reference=50, score_min=300, score_max=850
)


def _produit(**overrides: object) -> ProduitCredit:
    values: dict[str, object] = {
        "produit_id": "PROD-1",
        "libelle": "Produit test",
        "segment": "individuel",
        "type_garantie": "individuelle",
        "montant_min": 50000,
        "montant_max": 1000000,
        "duree_min_mois": 3,
        "duree_max_mois": 24,
        "taux_annuel": 0.18,
    }
    values.update(overrides)
    return ProduitCredit(**values)  # type: ignore[arg-type]


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
class _FakeCoreSimReader:
    produits: list[ProduitCredit] = field(default_factory=list)

    def charger_produits(self) -> list[ProduitCredit]:
        return self.produits


@dataclass
class _FakeGrilleRepository:
    configuration: ConfigurationGrille

    def lire_active(self) -> ConfigurationGrille:
        return self.configuration


def test_un_produit_sans_correspondance_garde_objet_implicite_a_none() -> None:
    use_case = ListerProduits(
        core_sim_reader=_FakeCoreSimReader(produits=[_produit(produit_id="PROD-1")]),
        grille_repository=_FakeGrilleRepository(_configuration()),
    )

    resultat = use_case.execute()

    assert resultat[0].objet_implicite is None


def test_un_produit_reference_dans_la_grille_recoit_son_objet_implicite() -> None:
    use_case = ListerProduits(
        core_sim_reader=_FakeCoreSimReader(
            produits=[_produit(produit_id="PROD-AGRICOLE"), _produit(produit_id="PROD-1")]
        ),
        grille_repository=_FakeGrilleRepository(
            _configuration(objets_implicites_produits={"PROD-AGRICOLE": "intrants_agricoles"})
        ),
    )

    resultat = {p.produit_id: p.objet_implicite for p in use_case.execute()}

    assert resultat["PROD-AGRICOLE"] == "intrants_agricoles"
    assert resultat["PROD-1"] is None
