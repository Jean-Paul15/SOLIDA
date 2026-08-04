from typing import Literal

from pydantic import BaseModel

Segment = Literal["salarie", "individuel", "jeune", "femme_gie", "agricole"]
StatutSocietaire = Literal["actif", "inactif", "radie"]
StatutCredit = Literal["en_cours", "solde", "en_souffrance", "radie", "restructure"]
StatutGroupe = Literal["actif", "dissous", "en_difficulte"]
RoleGroupe = Literal["membre", "presidente", "tresoriere", "secretaire"]
NiveauInstruction = Literal["aucun", "primaire", "secondaire", "superieur"]
TendanceEpargne = Literal["hausse", "stable", "erosion"]
StatutCreditMembre = Literal["aucun_credit", "en_cours", "solde", "en_souffrance"]


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


class PointSolde(BaseModel):
    mois: str
    solde: int


class SyntheseEpargne(BaseModel):
    solde_moyen_6m: int
    tendance_12m: TendanceEpargne
    nb_mois_avec_depot_12m: int
    volatilite: float
    ratio_epargne_revenu: float
    anciennete_relation_mois: int
    serie_solde_12m: list[PointSolde]


class CreditResume(BaseModel):
    credit_id: str
    date_deblocage: str
    montant_octroye: int
    duree_mois: int
    numero_cycle: int
    statut: StatutCredit
    capital_restant_du: int
    max_jours_retard: int


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


class DossierSocietaire(BaseModel):
    identite: IdentiteSocietaire
    activite: ActiviteEconomique
    epargne: SyntheseEpargne
    historique_credit: list[CreditResume]
    groupe: SyntheseGroupe | None = None
    alertes: list[str]
