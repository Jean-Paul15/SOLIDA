from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MembreGroupe:
    societaire_id: str
    nom_complet: str
    role: str
    """`membre` | `presidente` | `tresoriere` | `secretaire`."""
    anciennete_mois: int
    statut_credit: str
    """`aucun_credit` | `en_cours` | `solde` | `en_souffrance`."""
    caution_appelee: bool


@dataclass(frozen=True)
class GroupeCaution:
    """Snapshot du groupe, calculé du point de vue d'un sociétaire donné.

    Les agrégats (`taux_remboursement_groupe`, `nb_cycles_completes`,
    `nb_credits_anterieurs_soldes`) excluent toujours ce sociétaire : c'est la
    règle de 03-MODELE/04-cascade-et-cold-start.md, appliquée uniformément à
    l'affichage (E2, E5) et au calcul de la cascade, pas seulement au scoring.
    """

    groupe_id: str
    nom_groupe: str
    taille_actuelle: int
    date_creation: date
    taux_remboursement_groupe: float | None
    nb_cycles_completes: int
    nb_credits_anterieurs_soldes: int
    nb_sorties_12m: int
    statut: str
    """`actif` | `dissous` | `en_difficulte`."""
    membres: list[MembreGroupe]
