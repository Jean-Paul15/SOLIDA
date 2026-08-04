from dataclasses import dataclass


@dataclass(frozen=True)
class FeaturesIndividuelles:
    """Voir 01-ARCHITECTURE/05-contrats-interfaces.md, section 2."""

    anciennete_societaire_mois: int
    segment: str
    solde_epargne_moyen_6m: int
    nb_mois_avec_depot_12m: int
    tendance_epargne_12m: str
    """`hausse` | `stable` | `erosion`."""
    volatilite_epargne: float
    ratio_epargne_revenu: float
    ratio_epargne_montant: float
    anciennete_epargne_mois: int
    ratio_endettement: float
    nb_credits_anterieurs: int
    nb_incidents_anterieurs: int
    max_jours_retard_historique: int | None
    """`None` pour un primo-emprunteur : distinct de 0 (aucun retard observé)."""
    montant_max_rembourse: int | None
    numero_cycle: int
    parts_sociales_montant: int
    nb_personnes_a_charge: int


@dataclass(frozen=True)
class FeaturesSolidaires:
    """Voir 01-ARCHITECTURE/05-contrats-interfaces.md, section 2. `None` hors segment de groupe."""

    en_groupe: bool
    groupe_id: str | None
    taille_groupe: int | None
    taux_remboursement_groupe: float | None
    deja_secouru_par_groupe: bool | None
