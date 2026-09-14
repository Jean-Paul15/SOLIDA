"""Inférence SOCLE et décomposition exacte destinée au backend."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .artifact import ManifesteModele, charger_bundle
from .calibration import CalibrateurPlatt
from .catalogue import FeatureSpec, catalogue_par_identifiant


class ModeleSocle:
    """Adaptateur pur autour d'un bundle EBM contrôlé.

    Le nom `ModeleSocle` est conservé pour ne pas casser les imports existants ; la classe
    sert aussi bien au bundle SOCLE qu'au bundle enrichi, son catalogue de features étant
    déterminé par `manifeste.identifiant` (`catalogue_par_identifiant`).
    """

    def __init__(self, modele: Any, calibrateur: CalibrateurPlatt, manifeste: ManifesteModele) -> None:
        self._modele = modele
        self._calibrateur = calibrateur
        self._manifeste = manifeste
        self._catalogue: tuple[FeatureSpec, ...] = catalogue_par_identifiant(manifeste.identifiant)
        self._codes: list[str] = [feature.code for feature in self._catalogue]

    @classmethod
    def depuis_dossier(cls, dossier: Path) -> ModeleSocle:
        modele, calibrateur, manifeste = charger_bundle(dossier)
        return cls(modele, calibrateur, manifeste)

    @property
    def identifiant(self) -> str:
        return self._manifeste.identifiant

    @property
    def version(self) -> str:
        return self._manifeste.version

    @property
    def checksum(self) -> str:
        return self._manifeste.checksum_modele

    @property
    def codes(self) -> list[str]:
        """Catalogue de features effectivement attendu par ce bundle (SOCLE ou enrichi)."""
        return list(self._codes)

    def _dataframe(self, features: Mapping[str, object]) -> pd.DataFrame:
        inconnues = set(features).difference(self._codes)
        if inconnues:
            raise ValueError(f"Features {self._manifeste.identifiant!r} inconnues : {sorted(inconnues)}")
        ligne = {code: features.get(code, np.nan) for code in self._codes}
        frame = pd.DataFrame([ligne])
        for spec in self._catalogue:
            if spec.type_ebm == "continue":
                frame[spec.code] = pd.to_numeric(frame[spec.code], errors="coerce")
            else:
                frame[spec.code] = frame[spec.code].astype("object").where(
                    frame[spec.code].notna(), np.nan
                )
        return frame

    def predire(self, features: Mapping[str, object]) -> float:
        frame = self._dataframe(features)
        p_brute = float(self._modele.predict_proba(frame)[0, 1])
        logit = np.log(np.clip(p_brute, 1e-8, 1 - 1e-8) / np.clip(1 - p_brute, 1e-8, 1 - 1e-8))
        return float(self._calibrateur.predire(np.asarray([logit]))[0])

    def contributions_log_odds_bon(self, features: Mapping[str, object]) -> list[tuple[str, float]]:
        """Retourne les contributions dans la convention bancaire bon/mauvais."""
        frame = self._dataframe(features)
        contributions_termes = np.asarray(self._modele.eval_terms(frame))[0]
        par_feature: defaultdict[str, float] = defaultdict(float)
        termes = getattr(self._modele, "term_features_", None)
        if termes is None:
            raise ValueError("Le bundle EBM ne contient pas les termes explicables attendus.")
        noms = self._codes
        for indexes, contribution in zip(termes, contributions_termes, strict=True):
            repartition = self._calibrateur.contribution_bon(float(contribution)) / len(indexes)
            for index in indexes:
                par_feature[noms[int(index)]] += repartition
        return [(code, par_feature[code]) for code in noms if code in par_feature]
