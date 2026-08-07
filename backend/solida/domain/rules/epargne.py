SEUIL_HAUSSE = 0.10  # voir docs/formules/
SEUIL_EROSION = -0.05


def tendance_depuis_croissance(croissance_12m: float) -> str:
    """`hausse` | `stable` | `erosion`, à partir de la croissance de l'épargne sur 12 mois."""
    if croissance_12m > SEUIL_HAUSSE:
        return "hausse"
    if croissance_12m < SEUIL_EROSION:
        return "erosion"
    return "stable"
