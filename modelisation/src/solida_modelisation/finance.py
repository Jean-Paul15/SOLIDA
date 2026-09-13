"""Calculs financiers partagés entre entraînement et inférence."""

import math


def mensualite_actuarielle(montant: float, duree_mois: int, taux_annuel: float) -> float:
    """Mensualité d'un prêt amortissable à échéances constantes, sans frais."""
    if montant < 0:
        raise ValueError("Le montant doit être positif.")
    if duree_mois <= 0:
        raise ValueError("La durée doit être strictement positive.")
    taux_mensuel = taux_annuel / 12
    if taux_mensuel == 0:
        return montant / duree_mois
    facteur = math.pow(1 + taux_mensuel, duree_mois)
    return montant * taux_mensuel * facteur / (facteur - 1)
