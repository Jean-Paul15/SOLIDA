"""Calibration Platt conservant une décomposition additive des log-odds."""

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression


@dataclass
class CalibrateurPlatt:
    """Calibrateur sur le logit de défaut ; identité lorsqu'il n'est pas nécessaire."""

    actif: bool = False
    coefficient: float = 1.0
    intercept: float = 0.0

    def fit(self, logits_defaut: np.ndarray, cible: np.ndarray) -> "CalibrateurPlatt":
        modele = LogisticRegression(C=1_000_000.0, solver="lbfgs", max_iter=2_000, random_state=42)
        modele.fit(logits_defaut.reshape(-1, 1), cible)
        self.actif = True
        self.coefficient = float(modele.coef_[0, 0])
        self.intercept = float(modele.intercept_[0])
        return self

    def predire(self, logits_defaut: np.ndarray) -> np.ndarray:
        logits = self.coefficient * logits_defaut + self.intercept
        return 1.0 / (1.0 + np.exp(-logits))

    def log_odds_bon(self, logit_defaut: float) -> float:
        """Passe du logit calibré de défaut au log-odds bancaire bon/mauvais."""
        return -(self.coefficient * logit_defaut + self.intercept)

    def contribution_bon(self, contribution_logit_defaut: float) -> float:
        return -self.coefficient * contribution_logit_defaut
