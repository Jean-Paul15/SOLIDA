from pydantic import BaseModel, Field


class ParametresGrille(BaseModel):
    # Bornes reprises des sliders de l'ecran Politique de credit
    # (frontend/components/solida/PolitiqueCredit.tsx), imposees ici aussi cote serveur pour
    # qu'un appel API direct ne puisse pas les contourner.
    marge: float = Field(ge=0.05, le=0.30)
    lgd: float = Field(ge=0.40, le=0.90)
    multiplicateur_accord: float = Field(ge=0.30, le=0.95)
    # Valeur de repli alignee sur `ParametresGrille.plafond_institutionnel_fcfa` : un appel
    # qui omet le champ (anciens clients, tests existants) garde le maximum institutionnel
    # actuel plutot que d'echouer la validation.
    plafond_institutionnel_fcfa: int = Field(default=100_000_000, gt=0)
    # Valeur de demonstration (voir solida.domain.rules.grille.ParametresGrille), pas une
    # norme FUCEC ni BCEAO documentee : repli identique pour ne pas casser un appel existant.
    ratio_endettement_maximal: float = Field(default=0.33, gt=0, le=1)


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

    # max_length=30 aligne sur la colonne `varchar(30)` (cle primaire) de `grille_decision` :
    # un depassement doit etre rejete proprement ici, avant d'atteindre la base.
    version_grille: str = Field(min_length=1, max_length=30)
    grille: ParametresGrille
    progressif: ParametresProgressif
    scorecard: ParametresScorecard
