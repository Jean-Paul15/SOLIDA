from typing import Literal

from pydantic import BaseModel

StatutGroupe = Literal["actif", "dissous", "en_difficulte"]
RoleGroupe = Literal["membre", "presidente", "tresoriere", "secretaire"]
StatutCreditMembre = Literal["aucun_credit", "en_cours", "solde", "en_souffrance"]


class MembreGroupe(BaseModel):
    societaire_id: str
    nom_complet: str
    role: RoleGroupe
    anciennete_mois: int
    statut_credit: StatutCreditMembre
    caution_appelee: bool


class SyntheseGroupe(BaseModel):
    groupe_id: str
    nom_groupe: str
    taille_actuelle: int
    date_creation: str
    taux_remboursement_groupe: float | None
    nb_cycles_completes: int
    nb_sorties_12m: int
    statut: StatutGroupe
    membres: list[MembreGroupe]
