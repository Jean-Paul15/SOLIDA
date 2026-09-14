"""J2-10b : modèle direct, API, fiche doivent produire la même probabilité, le même score
et les mêmes contributions pour un même dossier.

Le calcul "modèle direct" réutilise les fonctions réelles de `scorer_demande_features.py`
(les mêmes que `ScorerDemande._calculate`) pour construire le dictionnaire de features : ce
test vérifie que le chemin HTTP ne change rien à ce calcul, pas qu'une réimplémentation
indépendante retombe sur le même résultat par coïncidence.
"""

import math
import os
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from solida.application.use_cases.scorer_demande_features import (
    _actualiser_features,
    _features_to_dict,
    _revenu_effectif,
)
from solida.domain.rules.scorecard import calculer_score, decomposer_en_points
from solida.domain.values.demande import DemandeScoring
from solida.domain.values.probabilite import ProbabiliteDefaut
from solida.infrastructure.application_fastapi import app
from solida.infrastructure.dependencies.adapters import (
    core_sim_reader,
    feature_store,
    grille_repository,
    scoring_model,
)

pytestmark = pytest.mark.skipif(
    "SOLIDA_DATABASE_URL_ASYNC" not in os.environ or "CORESIM_DATABASE_URL" not in os.environ,
    reason="Bases reelles absentes : integration non disponible ici",
)


@pytest.fixture
def client_agent() -> TestClient:
    client = TestClient(app)
    client.post(
        "/api/v1/auth/login", json={"identifiant": "agent.be", "mot_de_passe": "solida-demo"}
    )
    return client


@pytest.fixture
def societaire_individuel() -> str:
    # Hors groupe : le mode SOCLE est garanti, donc un seul modèle est en jeu des deux côtés
    # de la comparaison (pas de dépendance à l'éligibilité de la cascade pour ce test).
    moteur = create_engine(os.environ["CORESIM_DATABASE_URL"])
    with moteur.connect() as connexion:
        ligne = connexion.execute(
            text("""
                SELECT s.societaire_id FROM societaires s
                WHERE s.caisse_id = 'CAI-00' AND s.gie_id IS NULL AND NOT EXISTS (
                    SELECT 1 FROM credits c
                    WHERE c.societaire_id = s.societaire_id AND c.statut = 'en_cours'
                )
                ORDER BY random() LIMIT 1
            """)
        ).first()
    assert ligne is not None
    return ligne.societaire_id


def _demande_dict(societaire_id: str) -> dict[str, object]:
    return {
        "societaire_id": societaire_id,
        "produit_id": "prod-individuel",
        "montant_demande": 100_000,
        "duree_demandee_mois": 6,
        "objet_credit": "stock",
    }


def test_modele_api_et_fiche_donnent_la_meme_probabilite_et_les_memes_contributions(
    client_agent: TestClient, societaire_individuel: str
) -> None:
    # --- (a) modèle direct : mêmes fonctions de construction de features que ScorerDemande ---
    reader = core_sim_reader()
    store = feature_store()
    modele = scoring_model()

    societaire = reader.charger_societaire(societaire_individuel)
    assert societaire is not None
    produit = next(p for p in reader.charger_produits() if p.produit_id == "prod-individuel")
    date_reference = datetime.now(UTC).date()
    features_individuelles = store.lire_individuelles(societaire_individuel, date_reference)
    assert features_individuelles is not None

    demande = DemandeScoring(
        societaire_id=societaire_individuel,
        produit_id="prod-individuel",
        montant_demande=100_000,
        duree_demandee_mois=6,
        objet_credit="stock",
        groupe_id=None,
        actualisation=None,
    )
    revenu_effectif = _revenu_effectif(demande, societaire.revenu_mensuel_declare)
    features_actualisees = _actualiser_features(
        features_individuelles, demande, revenu_effectif, produit.taux_annuel
    )
    features_dict = _features_to_dict(features_actualisees, demande)

    probabilite_directe = ProbabiliteDefaut(modele.predire(features_dict).valeur)
    contributions_directes = modele.contributions(features_dict)

    # Reproduit exactement le calcul de `ScorerDemande._calculate` (même grille active, même
    # transformation PDO) pour obtenir le score et la décomposition attendus, sans recopier une
    # formule indépendante qui pourrait diverger sans qu'on s'en aperçoive.
    configuration = grille_repository().lire_active()
    score_direct = calculer_score(probabilite_directe, configuration.scorecard)
    beta_0 = math.log((1 - probabilite_directe.valeur) / probabilite_directe.valeur) - sum(
        v for _, v in contributions_directes
    )
    points_de_base_direct, points_directs = decomposer_en_points(
        beta_0, contributions_directes, configuration.scorecard
    )
    points_directs_par_code = {p.code_variable: p.points for p in points_directs}

    # --- (b) API : /preview passe par ScorerDemande._calculate en entier ---
    reponse_preview = client_agent.post(
        "/api/v1/scoring/preview", json=_demande_dict(societaire_individuel)
    )
    assert reponse_preview.status_code == 200
    resultat_preview = reponse_preview.json()

    assert resultat_preview["score"] == pytest.approx(score_direct.valeur, abs=1e-6)
    assert resultat_preview["points_de_base"] == pytest.approx(points_de_base_direct, abs=1e-6)
    for contribution in resultat_preview["decomposition"]:
        assert contribution["points"] == pytest.approx(
            points_directs_par_code[contribution["code_variable"]], abs=1e-6
        )

    # --- (c) confirmation puis fiche : même score que (a) et (b) ---
    reponse_confirm = client_agent.post(
        "/api/v1/scoring/confirm", json=_demande_dict(societaire_individuel)
    )
    assert reponse_confirm.status_code == 201
    resultat_confirm = reponse_confirm.json()
    assert resultat_confirm["score"] == pytest.approx(score_direct.valeur, abs=1e-6)

    decision_id = resultat_confirm["decision_id"]
    reponse_fiche = client_agent.get(f"/api/v1/scoring/{decision_id}/fiche")
    assert reponse_fiche.status_code == 200
    fiche = reponse_fiche.json()
    assert fiche["resultat"]["score"] == pytest.approx(score_direct.valeur, abs=1e-6)
    for contribution in fiche["facteurs_favorables"] + fiche["facteurs_defavorables"]:
        assert contribution["points"] == pytest.approx(
            points_directs_par_code[contribution["code_variable"]], abs=1e-6
        )
