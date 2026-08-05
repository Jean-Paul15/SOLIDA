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


@dataclass(frozen=True)
class MouvementEpargneAffiche:
    date_operation: date
    sens: str
    """`depot` | `retrait`."""
    montant: int


@dataclass(frozen=True)
class SyntheseEpargne:
    solde_moyen_6m: int
    tendance_12m: str
    nb_mois_avec_depot_12m: int
    volatilite: float
    ratio_epargne_revenu: float
    anciennete_relation_mois: int
    # Échantillon réel de mouvements récents (pas une courbe de solde reconstruite, voir
    # docs/backend/03-decisions-provisoires-a-revoir.md) : pas une série complète.
    mouvements_recents: list[MouvementEpargneAffiche]


@dataclass(frozen=True)
class CreditResume:
    credit_id: str
    date_deblocage: date
    montant_octroye: int
    duree_mois: int
    numero_cycle: int
    statut: str
    capital_restant_du: int
    max_jours_retard: int


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


@dataclass(frozen=True)
class DossierSocietaire:
    identite: IdentiteSocietaire
    activite: ActiviteEconomique
    epargne: SyntheseEpargne
    historique_credit: list[CreditResume]
    groupe: SyntheseGroupe | None
    alertes: list[str]
