from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class IdentiteSocietaire:
    societaire_id: str
    numero_membre: str
    nom_complet: str
    segment: str
    agence: str
    date_adhesion: date
    anciennete_mois: int
    statut: str
    age: int
    niveau_instruction: str | None


@dataclass(frozen=True)
class ActiviteEconomique:
    secteur: str
    anciennete_activite_mois: int
    revenu_mensuel_declare: int | None
    charges_mensuelles: int | None
    capacite_remboursement_estimee: int
    nb_personnes_a_charge: int
    parts_sociales_montant: int
