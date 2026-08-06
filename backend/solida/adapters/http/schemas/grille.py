from pydantic import BaseModel, Field


class ParametresGrille(BaseModel):
    marge: float = Field(gt=0)
    lgd: float = Field(gt=0)
    multiplicateur_accord: float
    multiplicateur_vigilance: float
    multiplicateur_examen: float


class ParametresProgressif(BaseModel):
    coefficient_progression: float
    montant_plancher: int = Field(ge=0)
    plafond_primo_emprunteur: int = Field(ge=0)
    plafonds_produits: dict[str, int]
    modulation_base: float
    modulation_pente: float
    modulation_min: float
    modulation_max: float


class ParametresScorecard(BaseModel):
    pdo: float = Field(gt=0)
    score_reference: float
    odds_reference: float = Field(gt=0)


class ConfigurationGrille(BaseModel):
    version_grille: str
    grille: ParametresGrille
    progressif: ParametresProgressif
    scorecard: ParametresScorecard
    auteur: str
    date_activation: str
    active: bool


class NouvelleConfigurationGrille(BaseModel):
    """Sans `date_activation` ni `active` : imposés par le dépôt, pas choisis par l'appelant."""

    version_grille: str
    grille: ParametresGrille
    progressif: ParametresProgressif
    scorecard: ParametresScorecard
