"""Parité entraînement / inférence pour la couche solidaire (J2-08b).

`CRD-012071` (GIE-0357, référence 2026-07-02) a été choisi dans le jeu d'entraînement
(`modelisation/data/jeux/jeu_enrichi.parquet`, construit depuis les parquet du simulateur)
pour son historique de groupe non trivial (15 crédits antérieurs, 3 incidents, 2 cautions
appelées). Les valeurs attendues ci-dessous sont celles produites par
`solida_modelisation.features.construire_jeu_enrichi` sur ce même crédit — le test vérifie
que le chemin d'inférence (Postgres + `calculer_features_groupe`) reproduit exactement les
mêmes six variables à partir de la même donnée brute, chargée autrement.
"""

import os
from datetime import date

import pytest
from solida_modelisation.features_groupe import calculer_features_groupe
from sqlalchemy import create_engine

from solida.adapters.core_sim.postgres_donnees_groupe_reader import PostgresDonneesGroupeReader

pytestmark = pytest.mark.skipif(
    "CORESIM_DATABASE_URL" not in os.environ,
    reason="CORESIM_DATABASE_URL absent : integration reelle non disponible dans cet environnement",
)

GIE_REFERENCE = "GIE-0357"
DATE_REFERENCE = date(2026, 7, 2)  # date_deblocage de CRD-012071

# Valeurs produites par modelisation.construire_jeu_enrichi pour CRD-012071.
ATTENDU = {
    "taille_groupe": 14,
    "anciennete_groupe_mois": 155,
    "nb_credits_groupe_anterieurs": 15,
    "nb_incidents_groupe_anterieurs": 3,
    "max_jours_retard_groupe_6m": 0.0,
    "nb_cautions_appelees_anterieures": 2,
}


@pytest.fixture(scope="module")
def donnees_groupe_reader() -> PostgresDonneesGroupeReader:
    engine = create_engine(os.environ["CORESIM_DATABASE_URL"])
    return PostgresDonneesGroupeReader(engine)


def test_features_groupe_identiques_entre_entrainement_et_inference(
    donnees_groupe_reader: PostgresDonneesGroupeReader,
) -> None:
    donnees = donnees_groupe_reader.charger_donnees_groupe(GIE_REFERENCE)
    assert donnees is not None

    resultat = calculer_features_groupe(
        date_reference=DATE_REFERENCE,
        date_creation_groupe=donnees.date_creation,
        appartenances=donnees.appartenances,
        credits_anterieurs=donnees.credits_anterieurs,
        echeances_groupe=donnees.echeances_groupe,
        cautions_anterieures=donnees.cautions_anterieures,
    )

    assert resultat.taille_groupe == ATTENDU["taille_groupe"]
    assert resultat.anciennete_groupe_mois == ATTENDU["anciennete_groupe_mois"]
    assert resultat.nb_credits_groupe_anterieurs == ATTENDU["nb_credits_groupe_anterieurs"]
    assert resultat.nb_incidents_groupe_anterieurs == ATTENDU["nb_incidents_groupe_anterieurs"]
    assert resultat.max_jours_retard_groupe_6m == ATTENDU["max_jours_retard_groupe_6m"]
    assert resultat.nb_cautions_appelees_anterieures == ATTENDU["nb_cautions_appelees_anterieures"]


def test_demande_individuelle_hors_groupe_ne_recoit_aucune_variable_de_groupe() -> None:
    """Arbitrage 2026-09-14 : une demande individuelle n'a jamais de couche solidaire,
    même si le sociétaire appartient par ailleurs à un GIE."""
    from solida.domain.rules.cascade import ContexteCascade, ParametresCascade, determiner_mode
    from solida.domain.values.mode_calcul import ModeCalcul

    resultat = determiner_mode(
        ContexteCascade(
            appartient_a_un_groupe=False,
            taille_groupe=0,
            nb_credits_anterieurs_groupe_soldes=0,
            fraicheur_features_jours=0,
        ),
        ParametresCascade(),
    )
    assert resultat.mode == ModeCalcul.SOCLE_SEUL
