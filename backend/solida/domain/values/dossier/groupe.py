from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MembreGroupeAffiche:
    societaire_id: str
    nom_complet: str
    role: str
    anciennete_mois: int
    statut_credit: str
    caution_appelee: bool


@dataclass(frozen=True)
class SyntheseGroupe:
    groupe_id: str
    nom_groupe: str
    taille_actuelle: int
    date_creation: date
    taux_remboursement_groupe: float | None
    nb_cycles_completes: int
    nb_sorties_12m: int
    statut: str
    membres: list[MembreGroupeAffiche]
