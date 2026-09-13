"""Pont DVC vers le générateur CORE-SIM existant, sans dupliquer sa logique."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sortie", type=Path, required=True)
    arguments = parser.parse_args()
    racine = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(racine / "simulateur" / "simulateur"))
    from pipeline import charger_config, ecrire_sorties, generer_donnees  # type: ignore[import-not-found]

    configuration = charger_config()
    ecrire_sorties(generer_donnees(configuration), arguments.sortie)


if __name__ == "__main__":
    main()
