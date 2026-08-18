from typing import Literal

from pydantic import BaseModel

Segment = Literal["salarie", "individuel", "jeune", "femme_gie", "agricole"]
StatutSocietaire = Literal["actif", "inactif", "radie"]
NiveauInstruction = Literal["aucun", "primaire", "secondaire", "superieur"]


class ResultatRechercheSocietaire(BaseModel):
    societaire_id: str
    nom_complet: str
    numero_membre: str
    agence: str
    zone: str
    statut: StatutSocietaire
    a_credit_en_cours: bool


class IdentiteSocietaire(BaseModel):
    societaire_id: str
    numero_membre: str
    nom_complet: str
    segment: Segment
    agence: str
    date_adhesion: str
    anciennete_mois: int
    statut: StatutSocietaire
    age: int
    niveau_instruction: NiveauInstruction | None = None


class ActiviteEconomique(BaseModel):
    secteur: str
    anciennete_activite_mois: int
    revenu_mensuel_declare: int | None = None
    charges_mensuelles: int | None = None
    capacite_remboursement_estimee: int
    nb_personnes_a_charge: int
    parts_sociales_montant: int
