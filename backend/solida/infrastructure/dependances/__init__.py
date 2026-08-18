"""Racine de composition, scindée par sous-domaine (voir `adapters.py` pour les fabriques
partagées). Réexporte tout pour que les routeurs continuent d'écrire
`from solida.infrastructure.dependances import xxx` sans connaître ce découpage interne.
"""

from solida.infrastructure.dependances.adapters import audit_log, fiche_pdf_generator
from solida.infrastructure.dependances.grille import lire_grille_active, modifier_grille
from solida.infrastructure.dependances.produits import lister_produits
from solida.infrastructure.dependances.registre import lister_decisions
from solida.infrastructure.dependances.scoring import (
    archiver_fiche,
    generer_fiche,
    lire_decision,
    scorer_demande,
)
from solida.infrastructure.dependances.societaires import (
    consulter_dossier,
    lister_societaires_recents,
    rechercher_societaire,
)

__all__ = [
    "archiver_fiche",
    "audit_log",
    "consulter_dossier",
    "fiche_pdf_generator",
    "generer_fiche",
    "lire_decision",
    "lire_grille_active",
    "lister_decisions",
    "lister_produits",
    "lister_societaires_recents",
    "modifier_grille",
    "rechercher_societaire",
    "scorer_demande",
]
