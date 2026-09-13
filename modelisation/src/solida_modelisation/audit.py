"""Contrôles explicites avant toute revue d'un modèle SOCLE."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .catalogue import COLONNES_INTERDITES, codes_features_socle


def auditer_risque_fuite(
    dataset: pd.DataFrame, metriques_test: dict[str, float]
) -> dict[str, Any]:
    """Produit une preuve d'audit, sans dissimuler une performance anormalement élevée."""
    features = set(codes_features_socle())
    colonnes_resultat = {
        "defaut",
        "statut",
        "jours_retard",
        "date_paiement_reelle",
        "date_issue",
    }
    classes_attendues = {"bon", "defaut", "indetermine", "en_cours"}
    controles = {
        "signature_sans_colonne_interdite": not bool(features.intersection(COLONNES_INTERDITES)),
        "signature_sans_resultat_credit_evalue": not bool(features.intersection(colonnes_resultat)),
        "date_reference_non_future": bool(
            (pd.to_datetime(dataset["date_reference"]) <= pd.Timestamp("2026-08-01")).all()
        ),
        "classes_cible_attendues": set(dataset["classe_cible"].dropna().unique()) <= classes_attendues,
        "pas_de_cible_binaire_sur_indetermine_ou_en_cours": bool(
            dataset.loc[
                dataset["classe_cible"].isin(["indetermine", "en_cours"]), "cible"
            ].isna().all()
        ),
    }
    auc = metriques_test.get("auc", 0.0)
    return {
        "controles": controles,
        "auc_test": auc,
        "audit_renforce_requis": auc > 0.88,
        "motif": (
            "AUC test strictement supérieure à 0,88 : revue humaine de fuite requise."
            if auc > 0.88
            else None
        ),
        "conclusion": "conforme" if all(controles.values()) else "anomalie_detectee",
    }
