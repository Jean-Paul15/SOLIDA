from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Societaire:
    """Instantané des données brutes CORE-SIM pour un sociétaire.

    Ne porte jamais le sexe ni le statut matrimonial : engagement de
    non-discrimination, même si ces colonnes existent dans le générateur.
    """

    societaire_id: str
    numero_membre: str
    nom_complet: str
    agence: str
    date_adhesion: date
    anciennete_mois: int
    segment: str
    age: int
    zone: str
    nb_personnes_a_charge: int
    niveau_instruction: str | None
    parts_sociales_montant: int
    revenu_mensuel_declare: int | None
    groupe_id: str | None
