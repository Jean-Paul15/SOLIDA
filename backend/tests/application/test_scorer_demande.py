from dataclasses import dataclass, field, fields
from datetime import UTC, date, datetime

import pytest

from solida.application.use_cases.scorer_demande import ScorerDemande
from solida.domain.entities.groupe import GroupeCaution
from solida.domain.entities.produit_credit import ProduitCredit
from solida.domain.entities.societaire import Societaire
from solida.domain.errors import (
    AccesRefuse,
    DonneesInsuffisantes,
    DureeDemandeeInvalide,
    MontantDemandeInvalide,
    ProduitIntrouvable,
    SocietaireIntrouvable,
    SurEndettement,
)
from solida.domain.rules.grille import ParametresGrille
from solida.domain.rules.progressif_plafond import ParametresProgressif
from solida.domain.rules.scorecard import ParametresScorecard
from solida.domain.values.decision import DecisionAEnregistrer, DecisionEnregistree
from solida.domain.values.demande import DemandeScoring
from solida.domain.values.features import FeaturesIndividuelles, FeaturesSolidaires
from solida.domain.values.grille import ConfigurationGrille
from solida.domain.values.montant import Montant
from solida.domain.values.probabilite import ProbabiliteDefaut

# --- Fixtures partagées ---

_NON_FOURNI = object()
"""Sentinel distinct de `None` : un paramètre de `_build_use_case` explicitement mis à `None`
(ex. `societaire=None` pour un sociétaire introuvable) ne doit pas retomber sur le défaut."""

PARAMETRES_SCORECARD = ParametresScorecard(
    pdo=20, score_reference=600, odds_reference=50, score_min=300, score_max=850
)


def _societaire(**overrides: object) -> Societaire:
    values: dict[str, object] = {
        "societaire_id": "SOC-1",
        "numero_membre": "100001",
        "nom_complet": "Test Societaire",
        "agence": "CAI-00",
        "date_adhesion": date(2020, 1, 1),
        "anciennete_mois": 48,
        "segment": "individuel",
        "age": 35,
        "zone": "urbain",
        "nb_personnes_a_charge": 2,
        "niveau_instruction": None,
        "parts_sociales_montant": 10000,
        "revenu_mensuel_declare": 150000,
        "groupe_id": None,
        "a_credit_en_cours": False,
    }
    values.update(overrides)
    return Societaire(**values)  # type: ignore[arg-type]


def _produit(**overrides: object) -> ProduitCredit:
    values: dict[str, object] = {
        "produit_id": "PROD-1",
        "libelle": "Produit test",
        "type_garantie": "individuelle",
        "montant_min": 50000,
        "montant_max": 1000000,
        "duree_min_mois": 3,
        "duree_max_mois": 24,
        "taux_annuel": 0.18,
    }
    values.update(overrides)
    return ProduitCredit(**values)  # type: ignore[arg-type]


def _demande(**overrides: object) -> DemandeScoring:
    values: dict[str, object] = {
        "societaire_id": "SOC-1",
        "produit_id": "PROD-1",
        "montant_demande": 200000,
        "duree_demandee_mois": 12,
        "objet_credit": "tresorerie",
        "groupe_id": None,
        "actualisation": None,
    }
    values.update(overrides)
    return DemandeScoring(**values)  # type: ignore[arg-type]


def _features_individuelles(**overrides: object) -> FeaturesIndividuelles:
    values: dict[str, object] = {
        "anciennete_societaire_mois": 48,
        "segment": "individuel",
        "solde_epargne_moyen_6m": 100000,
        "nb_mois_avec_depot_12m": 10,
        "tendance_epargne_12m": "hausse",
        "volatilite_epargne": 0.1,
        "ratio_epargne_revenu": 0.5,
        "ratio_epargne_montant": 0.3,
        "anciennete_epargne_mois": 48,
        "ratio_endettement": 0.2,
        "nb_credits_anterieurs": 2,
        "nb_incidents_anterieurs": 0,
        "max_jours_retard_historique": 0,
        "montant_max_rembourse": 150000,
        "numero_cycle": 2,
        "parts_sociales_montant": 10000,
        "nb_personnes_a_charge": 2,
    }
    values.update(overrides)
    return FeaturesIndividuelles(**values)  # type: ignore[arg-type]


def _features_solidaires(**overrides: object) -> FeaturesSolidaires:
    values: dict[str, object] = {
        "en_groupe": False,
        "groupe_id": None,
        "taille_groupe": None,
        "taux_remboursement_groupe": None,
        "deja_secouru_par_groupe": False,
    }
    values.update(overrides)
    return FeaturesSolidaires(**values)  # type: ignore[arg-type]


def _configuration(**overrides: object) -> ConfigurationGrille:
    values: dict[str, object] = {
        "version_grille": "v1",
        "grille": ParametresGrille(marge=0.1, lgd=0.5),
        "progressif": ParametresProgressif(
            coefficient_progression=1.5,
            montant_plancher=Montant(50000),
            plafond_primo_emprunteur=Montant(150000),
            plafonds_produits={"PROD-1": Montant(500000)},
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
    societaire: Societaire | None
    groupe: GroupeCaution | None = None
    produits: list[ProduitCredit] = field(default_factory=lambda: [_produit()])

    def charger_societaire(self, societaire_id: str) -> Societaire | None:
        return self.societaire

    def charger_groupe(self, societaire_id: str) -> GroupeCaution | None:
        return self.groupe

    def charger_produits(self) -> list[ProduitCredit]:
        return self.produits


@dataclass
class _FakeFeatureStore:
    individuelles: FeaturesIndividuelles | None
    solidaires: FeaturesSolidaires | None

    def lire_individuelles(self, societaire_id: str) -> FeaturesIndividuelles | None:
        return self.individuelles

    def lire_solidaires(self, societaire_id: str) -> FeaturesSolidaires | None:
        return self.solidaires


@dataclass
class _FakeScoringModel:
    probabilite: float = 0.05
    version_str: str = "v-test"

    def predire(self, features: dict[str, float]) -> ProbabiliteDefaut:
        return ProbabiliteDefaut(self.probabilite)

    def contributions(self, features: dict[str, float]) -> list[tuple[str, float]]:
        return [(code, 0.01) for code in features]

    def version(self) -> str:
        return self.version_str


@dataclass
class _FakeGrilleRepository:
    configuration: ConfigurationGrille

    def lire_active(self) -> ConfigurationGrille:
        return self.configuration


@dataclass
class _FakeDecisionRepository:
    decision_existante: bool = False
    decisions_enregistrees: list[DecisionEnregistree] = field(default_factory=list)

    def existe_decision_accordee_depuis(
        self, societaire_id: str, depuis: datetime, entree_actuelle: dict[str, object]
    ) -> bool:
        return self.decision_existante

    def enregistrer(self, decision: DecisionAEnregistrer) -> DecisionEnregistree:
        values = {field.name: getattr(decision, field.name) for field in fields(decision)}
        enregistree = DecisionEnregistree(**values, horodatage=datetime.now(UTC))
        self.decisions_enregistrees.append(enregistree)
        return enregistree


@dataclass
class _FakeAuditLog:
    evenements: list[tuple[str, str, str, dict[str, object]]] = field(default_factory=list)

    def enregistrer_evenement(
        self,
        type_evenement: str,
        acteur_id: str,
        objet: str,
        details: dict[str, object],
        adresse_ip: str | None = None,
    ) -> None:
        self.evenements.append((type_evenement, acteur_id, objet, details))


def _build_use_case(
    societaire: Societaire | None | object = _NON_FOURNI,
    groupe: GroupeCaution | None = None,
    produits: list[ProduitCredit] | None = None,
    individuelles: FeaturesIndividuelles | None | object = _NON_FOURNI,
    solidaires: FeaturesSolidaires | None = None,
    configuration: ConfigurationGrille | None = None,
    decision_existante: bool = False,
    probabilite: float = 0.05,
) -> tuple[ScorerDemande, _FakeDecisionRepository, _FakeAuditLog]:
    decision_repository = _FakeDecisionRepository(decision_existante=decision_existante)
    audit_log = _FakeAuditLog()
    use_case = ScorerDemande(
        core_sim_reader=_FakeCoreSimReader(
            societaire=_societaire() if societaire is _NON_FOURNI else societaire,  # type: ignore[arg-type]
            groupe=groupe,
            produits=produits if produits is not None else [_produit()],
        ),
        feature_store=_FakeFeatureStore(
            individuelles=(
                _features_individuelles() if individuelles is _NON_FOURNI else individuelles
            ),  # type: ignore[arg-type]
            solidaires=solidaires if solidaires is not None else _features_solidaires(),
        ),
        scoring_model=_FakeScoringModel(probabilite=probabilite),
        grille_repository=_FakeGrilleRepository(
            configuration=configuration if configuration is not None else _configuration()
        ),
        decision_repository=decision_repository,
        audit_log=audit_log,
    )
    return use_case, decision_repository, audit_log


# --- ScorerDemande : validations (orchestration bout-en-bout) ---


def test_previsualiser_societaire_introuvable() -> None:
    use_case, _, _ = _build_use_case(societaire=None)

    with pytest.raises(SocietaireIntrouvable):
        use_case.preview(_demande(), {}, "agent-1", "Agent", "CAI-00")


def test_previsualiser_acces_refuse_hors_agence() -> None:
    use_case, _, _ = _build_use_case(societaire=_societaire(agence="CAI-00"))

    with pytest.raises(AccesRefuse):
        use_case.preview(_demande(), {}, "agent-1", "Agent", "CAI-07")


def test_previsualiser_refuse_un_credit_en_cours() -> None:
    use_case, _, _ = _build_use_case(societaire=_societaire(a_credit_en_cours=True))

    with pytest.raises(SurEndettement):
        use_case.preview(_demande(), {}, "agent-1", "Agent", "CAI-00")


def test_previsualiser_refuse_un_multi_octroi() -> None:
    use_case, _, _ = _build_use_case(decision_existante=True)

    with pytest.raises(SurEndettement):
        use_case.preview(_demande(), {}, "agent-1", "Agent", "CAI-00")


def test_previsualiser_refuse_des_donnees_insuffisantes() -> None:
    use_case, _, _ = _build_use_case(individuelles=None)

    with pytest.raises(DonneesInsuffisantes):
        use_case.preview(_demande(), {}, "agent-1", "Agent", "CAI-00")


def test_previsualiser_refuse_un_produit_absent_de_la_grille() -> None:
    configuration = _configuration(
        progressif=ParametresProgressif(
            coefficient_progression=1.5,
            montant_plancher=Montant(50000),
            plafond_primo_emprunteur=Montant(150000),
            plafonds_produits={},
        )
    )
    use_case, _, _ = _build_use_case(configuration=configuration)

    with pytest.raises(ProduitIntrouvable):
        use_case.preview(_demande(), {}, "agent-1", "Agent", "CAI-00")


def test_previsualiser_refuse_un_montant_au_dela_du_plafond() -> None:
    use_case, _, _ = _build_use_case()

    with pytest.raises(MontantDemandeInvalide):
        use_case.preview(_demande(montant_demande=600000), {}, "agent-1", "Agent", "CAI-00")


def test_previsualiser_refuse_un_produit_absent_du_catalogue() -> None:
    use_case, _, _ = _build_use_case(produits=[])

    with pytest.raises(ProduitIntrouvable):
        use_case.preview(_demande(), {}, "agent-1", "Agent", "CAI-00")


def test_previsualiser_refuse_une_duree_hors_bornes() -> None:
    use_case, _, _ = _build_use_case(produits=[_produit(duree_min_mois=3, duree_max_mois=24)])

    with pytest.raises(DureeDemandeeInvalide):
        use_case.preview(_demande(duree_demandee_mois=36), {}, "agent-1", "Agent", "CAI-00")


# --- ScorerDemande : chemin nominal ---


def test_previsualiser_accord_nominal_ne_persiste_rien() -> None:
    use_case, decision_repository, audit_log = _build_use_case(probabilite=0.05)

    decision = use_case.preview(_demande(), {}, "agent-1", "Agent", "CAI-00")

    assert decision.tranche == "accord"
    assert decision_repository.decisions_enregistrees == []
    assert audit_log.evenements[0][0] == "scoring_previsualise"


def test_confirmer_accord_persiste_et_journalise() -> None:
    use_case, decision_repository, audit_log = _build_use_case(probabilite=0.05)

    decision = use_case.confirm(_demande(), {}, "agent-1", "Agent", "CAI-00")

    assert decision.tranche == "accord"
    assert len(decision_repository.decisions_enregistrees) == 1
    assert audit_log.evenements[-1][0] == "scoring_confirme"


def test_previsualiser_refus_a_probabilite_elevee() -> None:
    use_case, _, _ = _build_use_case(probabilite=0.5)

    decision = use_case.preview(_demande(), {}, "agent-1", "Agent", "CAI-00")

    assert decision.tranche == "refus"
