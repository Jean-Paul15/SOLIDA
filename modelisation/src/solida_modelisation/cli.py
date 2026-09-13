"""Entrées de ligne de commande du module modelisation."""

import argparse
import json
import os
import subprocess
from pathlib import Path

import pandas as pd

from .audit import auditer_risque_fuite
from .catalogue import codes_features_socle
from .entrainement import (
    ecrire_rapport_resultat,
    entrainer_reference_logistique,
    entrainer_socle_ebm,
)
from .features import ecrire_jeu_socle
from .mlflow_tracking import journaliser_reference, journaliser_socle


def _commit_git() -> str:
    if commit := os.environ.get("GIT_COMMIT"):
        return commit
    try:
        resultat = subprocess.run(
            ["git", "rev-parse", "HEAD"], check=False, capture_output=True, text=True
        )
    except FileNotFoundError:
        return "inconnu"
    return resultat.stdout.strip() if resultat.returncode == 0 else "inconnu"


def main() -> None:
    parser = argparse.ArgumentParser(prog="solida-modele")
    commandes = parser.add_subparsers(dest="commande", required=True)
    features = commandes.add_parser("construire-features")
    features.add_argument("--source", type=Path, required=True)
    features.add_argument("--sortie", type=Path, required=True)
    features.add_argument("--date-fin", default="2026-08-01")
    entrainer = commandes.add_parser("entrainer")
    entrainer.add_argument("--dataset", type=Path, required=True)
    entrainer.add_argument("--sortie", type=Path, required=True)
    entrainer.add_argument("--modele", choices=["reference", "socle", "tous"], default="tous")
    arguments = parser.parse_args()

    if arguments.commande == "construire-features":
        dataset = ecrire_jeu_socle(arguments.source, arguments.sortie, pd.Timestamp(arguments.date_fin))
        print(dataset["classe_cible"].value_counts().to_string())
        return

    dataset = pd.read_parquet(arguments.dataset)
    if arguments.modele in {"reference", "tous"}:
        reference = entrainer_reference_logistique(dataset)
        ecrire_rapport_resultat(reference, arguments.sortie, "reference")
        journaliser_reference(
            reference.modele,
            reference.metriques_validation,
            reference.metriques_test,
            dataset[codes_features_socle()].head(10),
        )
    if arguments.modele in {"socle", "tous"}:
        socle = entrainer_socle_ebm(
            dataset,
            dossier_bundle=arguments.sortie / "bundle_socle",
            commit_git=_commit_git(),
        )
        ecrire_rapport_resultat(socle, arguments.sortie, "socle")
        (arguments.sortie / "socle_audit_fuite.json").write_text(
            json.dumps(
                auditer_risque_fuite(dataset, socle.metriques_test), ensure_ascii=False, indent=2
            ),
            encoding="utf-8",
        )
        journaliser_socle(
            socle.metriques_validation,
            socle.metriques_test,
            arguments.sortie / "bundle_socle",
            dataset[codes_features_socle()].head(10),
        )
        print(pd.Series(socle.metriques_test).to_string())


if __name__ == "__main__":
    main()
