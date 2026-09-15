from dataclasses import dataclass, field
from datetime import UTC, date, datetime

import pytest

from solida.application.use_cases.process_societaire_demande import ProcessSocietaireDemande
from solida.domain.entities.produit_credit import ProduitCredit
from solida.domain.entities.societaire import Societaire
from solida.domain.errors import ProduitIntrouvable
from solida.domain.rules.grille import ParametresGrille
from solida.domain.rules.progressif_plafond import ParametresProgressif
from solida.domain.rules.scorecard import ParametresScorecard
from solida.domain.values.demande import ActualisationSituation, DemandeScoring
from solida.domain.values.demande_societaire import (
    STATUT_NOUVELLE,
    DemandeSocietaire,
    DemandeSocietaireACreer,
)
from solida.domain.values.grille import ConfigurationGrille
from solida.domain.values.montant import Montant
from solida.domain.values.tranche import TrancheDecision

SECRET = "secret-test"


def _societaire(**overrides: object) -> Societaire:
    values: dict[str, object] = {
        "societaire_id": "SOC-1",
        "numero_membre": "M-1",
        "nom_complet": "Test Sociétaire",
        "agence": "CAI-00",
        "date_adhesion": date(2020, 1, 1),
        "anciennete_mois": 48,
        "segment": "individuel",
        "age": 40,
        "zone": "urbaine",
        "nb_personnes_a_charge": 2,
        "niveau_instruction": None,
        "parts_sociales_montant": 10000,
        "revenu_mensuel_declare": None,
        "groupe_id": None,
        "a_credit_en_cours": False,
    }
    values.update(overrides)
    return Societaire(**values)  # type: ignore[arg-type]


@dataclass
class _FakeCoreSimReader:
    societaire: Societaire
    produits: list[ProduitCredit] = field(default_factory=list)

    def charger_societaire(self, societaire_id: str) -> Societaire | None:
        return self.societaire

    def charger_produits(self) -> list[ProduitCredit]:
        return self.produits


@dataclass
class _DecisionFactice:
    """Duck-type minimal : `ProcessSocietaireDemande` ne lit que ces trois attributs sur ce
    que `scorer_demande.preview()` renvoie."""

    tranche: TrancheDecision = TrancheDecision.ACCORD
    montant_recommande: Montant = field(default_factory=lambda: Montant(valeur=100_000))
    conditions_reexamen: list[str] = field(default_factory=list)


@dataclass
class _FakeScorerDemande:
    demandes_recues: list[DemandeScoring] = field(default_factory=list)
    decision: _DecisionFactice = field(default_factory=_DecisionFactice)

    def preview(self, demande: DemandeScoring, **kwargs: object) -> _DecisionFactice:
        self.demandes_recues.append(demande)
        return self.decision


@dataclass
class _FakeDecisionRepository:
    agent_habituel_id: str | None = None

    def dernier_agent_reel(self, societaire_id: str) -> str | None:
        return self.agent_habituel_id


@dataclass
class _FakeDemandeSocietaireRepository:
    enregistrees: list[DemandeSocietaireACreer] = field(default_factory=list)

    def enregistrer(self, demande: DemandeSocietaireACreer) -> DemandeSocietaire:
        self.enregistrees.append(demande)
        return DemandeSocietaire(
            demande_id=demande.demande_id,
            societaire_id=demande.societaire_id,
            agence_id=demande.agence_id,
            montant_demande=demande.montant_demande,
            objet_credit=demande.objet_credit,
            duree_mois=demande.duree_mois,
            produit_id=demande.produit_id,
            resultat={},
            statut=STATUT_NOUVELLE,
            cree_le=datetime.now(UTC),
            assigne_a_agent_id=None,
            archivee_le=None,
            archivee_par_agent_id=None,
        )


@dataclass
class _FakeNotificationSender:
    notifiees: list[DemandeSocietaire] = field(default_factory=list)

    def notifier(self, demande: DemandeSocietaire) -> None:
        self.notifiees.append(demande)


@dataclass
class _FakeGrilleRepository:
    def lire_active(self) -> ConfigurationGrille:
        return ConfigurationGrille(
            version_grille="v1",
            grille=ParametresGrille(marge=0.1, lgd=0.5),
            progressif=ParametresProgressif(
                coefficient_progression=1.5,
                montant_plancher=Montant(50000),
                plafond_primo_emprunteur=Montant(150000),
                plafonds_produits={},
            ),
            scorecard=ParametresScorecard(
                pdo=20, score_reference=600, odds_reference=50, score_min=300, score_max=850
            ),
            auteur="test",
            date_activation=datetime.now(UTC),
            active=True,
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


def _build_use_case(
    agent_habituel_id: str | None = None,
    produits: list[ProduitCredit] | None = None,
    segment: str = "individuel",
) -> tuple[ProcessSocietaireDemande, _FakeScorerDemande, _FakeDemandeSocietaireRepository, str]:
    from solida.domain.rules.jeton_societaire import generer_jeton

    societaire = _societaire(segment=segment)
    scorer = _FakeScorerDemande()
    demande_societaire_repository = _FakeDemandeSocietaireRepository()
    use_case = ProcessSocietaireDemande(
        core_sim_reader=_FakeCoreSimReader(societaire, produits or []),
        scorer_demande=scorer,  # type: ignore[arg-type]
        demande_societaire_repository=demande_societaire_repository,
        decision_repository=_FakeDecisionRepository(agent_habituel_id),
        notification_sender=_FakeNotificationSender(),
        grille_repository=_FakeGrilleRepository(),
        secret=SECRET,
    )
    jeton = generer_jeton(SECRET, societaire.societaire_id)
    return use_case, scorer, demande_societaire_repository, jeton


def test_revenu_et_charges_declares_construisent_une_actualisation() -> None:
    use_case, scorer, _, jeton = _build_use_case()

    use_case.execute(
        jeton_session=jeton,
        montant_demande=200_000,
        objet_credit="fonds_roulement",
        duree_mois=12,
        produit_id="PROD-1",
        revenu_mensuel_declare=150_000,
        charges_mensuelles=50_000,
    )

    demande = scorer.demandes_recues[0]
    assert demande.actualisation == ActualisationSituation(
        revenu_mensuel_declare=150_000, charges_mensuelles=50_000
    )


def test_sans_revenu_ni_charges_actualisation_reste_absente() -> None:
    use_case, scorer, _, jeton = _build_use_case()

    use_case.execute(
        jeton_session=jeton,
        montant_demande=200_000,
        objet_credit="fonds_roulement",
        duree_mois=12,
        produit_id="PROD-1",
    )

    demande = scorer.demandes_recues[0]
    assert demande.actualisation is None


def test_societaire_avec_agent_habituel_est_assigne_directement() -> None:
    use_case, _, demande_societaire_repository, jeton = _build_use_case(
        agent_habituel_id="AGENT-1"
    )

    use_case.execute(
        jeton_session=jeton,
        montant_demande=200_000,
        objet_credit="fonds_roulement",
        duree_mois=12,
        produit_id="PROD-1",
    )

    demande = demande_societaire_repository.enregistrees[0]
    assert demande.assigne_a_agent_id == "AGENT-1"


def test_societaire_sans_historique_reste_non_assigne() -> None:
    use_case, _, demande_societaire_repository, jeton = _build_use_case(agent_habituel_id=None)

    use_case.execute(
        jeton_session=jeton,
        montant_demande=200_000,
        objet_credit="fonds_roulement",
        duree_mois=12,
        produit_id="PROD-1",
    )

    demande = demande_societaire_repository.enregistrees[0]
    assert demande.assigne_a_agent_id is None


def test_sans_produit_choisi_le_produit_se_deduit_du_segment() -> None:
    use_case, scorer, _, jeton = _build_use_case(
        segment="femme_gie",
        produits=[
            _produit(produit_id="PROD-INDIVIDUEL", segment="individuel"),
            _produit(produit_id="PROD-FEMME-GIE", segment="femme_gie"),
        ],
    )

    use_case.execute(
        jeton_session=jeton,
        montant_demande=200_000,
        objet_credit="fonds_roulement",
        duree_mois=12,
    )

    demande = scorer.demandes_recues[0]
    assert demande.produit_id == "PROD-FEMME-GIE"


def test_sans_produit_choisi_et_segment_ambigu_leve_une_erreur() -> None:
    use_case, _, _, jeton = _build_use_case(
        segment="individuel",
        produits=[
            _produit(produit_id="PROD-A", segment="individuel"),
            _produit(produit_id="PROD-B", segment="individuel"),
        ],
    )

    with pytest.raises(ProduitIntrouvable):
        use_case.execute(
            jeton_session=jeton,
            montant_demande=200_000,
            objet_credit="fonds_roulement",
            duree_mois=12,
        )
