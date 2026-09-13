from dataclasses import dataclass

type ValeurFeature = float | int | str | bool | None


@dataclass(frozen=True)
class FeaturesIndividuelles:
    anciennete_societaire_mois: int
    segment: str
    solde_epargne_moyen_6m: int
    nb_mois_avec_depot_12m: int
    tendance_epargne_12m: str
    """`hausse` | `stable` | `erosion`."""
    volatilite_epargne: float
    ratio_epargne_revenu: float | None
    ratio_epargne_montant: float
    anciennete_epargne_mois: int
    ratio_endettement: float | None
    nb_credits_anterieurs: int
    nb_incidents_anterieurs: int
    max_jours_retard_historique: int | None
    """`None` pour un primo-emprunteur : distinct de 0 (aucun retard observé)."""
    montant_max_rembourse: int | None
    numero_cycle: int
    parts_sociales_montant: int
    nb_personnes_a_charge: int
    zone_residence: str = "inconnue"
    revenu_mensuel_declare: int | None = None
    ratio_montant_historique: float | None = None


@dataclass(frozen=True)
class FeaturesSolidaires:
    """`None` pour un sociétaire hors segment de groupe."""

    en_groupe: bool
    groupe_id: str | None
    taille_groupe: int | None
    taux_remboursement_groupe: float | None
    deja_secouru_par_groupe: bool | None
