from typing import Literal

from pydantic import BaseModel, Field

ObjetCredit = Literal[
    "fonds_roulement",
    "equipement",
    "intrants_agricoles",
    "stock",
    "urgence_sante",
    "scolarite",
    "habitat",
    "autre",
]
Tranche = Literal["accord", "accord_sous_condition", "comite_de_credit", "refus"]
ModeCalcul = Literal["socle_seul", "enrichi"]


class ActualisationSituation(BaseModel):
    revenu_mensuel_declare: int | None = None
    charges_mensuelles: int | None = None
    nb_personnes_a_charge: int | None = None


class EntreeScoring(BaseModel):
    societaire_id: str
    produit_id: str
    montant_demande: int = Field(gt=0)
    # le=1200 (100 ans) : plafond technique anti-overflow, pas une borne produit — celle-ci
    # reste appliquee en aval via le catalogue CORE-SIM (duree_min_mois/duree_max_mois par
    # produit, scorer_demande.py).
    duree_demandee_mois: int = Field(gt=0, le=1200)
    objet_credit: ObjetCredit
    groupe_id: str | None = None
    actualisation: ActualisationSituation | None = None


class ContributionVariable(BaseModel):
    code_variable: str
    libelle: str
    valeur: str
    points: float
    sens: Literal["favorable", "defavorable", "neutre"]
    famille: Literal["profil", "activite", "epargne", "historique", "solidaire", "demande"]
    explication: str


class PalierProgression(BaseModel):
    cycle: int
    plafond_accessible: int


class ResultatScoring(BaseModel):
    decision_id: str
    societaire_id: str
    score: float
    tranche: Tranche
    montant_recommande: int
    montant_demande: int
    mode_calcul: ModeCalcul
    motif_mode: str | None = None
    decomposition: list[ContributionVariable]
    points_de_base: float
    plafond_progressif: int
    trajectoire_progression: list[PalierProgression]
    conditions_reexamen: list[str]
    version_modele: str
    version_grille: str
    horodatage: str
    avertissements: list[str]
