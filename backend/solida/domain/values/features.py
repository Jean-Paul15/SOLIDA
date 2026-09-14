from dataclasses import dataclass
from datetime import date

from solida_modelisation.features_groupe import (
    AppartenanceGie,
    CautionGroupe,
    CreditGroupeAnterieur,
    EcheanceGroupe,
)

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
    """Couche solidaire : historique du groupe emprunteur lui-même (arbitrage 2026-09-14,
    voir `précision.txt` réponses 1, 16, 21, 33) — jamais calculée pour une demande
    individuelle. `None` sur chaque champ hors `taille_groupe` si le groupe compte moins de
    membres que le seuil jugeable (réponse 22, `SEUIL_TAILLE_GROUPE_JUGEABLE`)."""

    taille_groupe: int | None
    anciennete_groupe_mois: int | None
    nb_credits_groupe_anterieurs: int | None
    nb_incidents_groupe_anterieurs: int | None
    max_jours_retard_groupe_6m: float | None
    nb_cautions_appelees_anterieures: int | None


@dataclass(frozen=True)
class DonneesGroupeBrutes:
    """Ce que `CoreSimReader.charger_donnees_groupe` doit fournir pour que
    `calculer_features_groupe` (partagée avec `modelisation`) puisse s'appliquer à
    l'identique côté inférence — c'est la garantie de parité entraînement/inférence
    (J2-08b), pas une duplication de logique."""

    date_creation: date
    appartenances: list[AppartenanceGie]
    credits_anterieurs: list[CreditGroupeAnterieur]
    echeances_groupe: list[EcheanceGroupe]
    cautions_anterieures: list[CautionGroupe]
