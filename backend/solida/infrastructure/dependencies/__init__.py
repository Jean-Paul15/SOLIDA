"""Racine de composition, scindée par sous-domaine (voir `adapters.py` pour les fabriques
partagées). Réexporte tout pour que les routers continuent d'écrire
`from solida.infrastructure.dependencies import xxx` sans connaître ce découpage interne.
"""

from solida.infrastructure.dependencies.adapters import audit_log, fiche_pdf_generator
from solida.infrastructure.dependencies.grille import lire_grille_active, modifier_grille
from solida.infrastructure.dependencies.notifications import (
    archiver_notification,
    assigner_notification,
    lister_notifications,
)
from solida.infrastructure.dependencies.portail import (
    authenticate_societaire,
    process_societaire_demande,
)
from solida.infrastructure.dependencies.produits import lister_produits
from solida.infrastructure.dependencies.registre import lister_decisions
from solida.infrastructure.dependencies.scoring import (
    archiver_fiche,
    generer_fiche,
    lire_decision,
    scorer_demande,
)
from solida.infrastructure.dependencies.societaires import (
    consulter_dossier,
    lister_societaires_recents,
    rechercher_societaire,
)

__all__ = [
    "archiver_fiche",
    "archiver_notification",
    "assigner_notification",
    "audit_log",
    "authenticate_societaire",
    "consulter_dossier",
    "fiche_pdf_generator",
    "generer_fiche",
    "lire_decision",
    "lire_grille_active",
    "lister_decisions",
    "lister_notifications",
    "lister_produits",
    "lister_societaires_recents",
    "modifier_grille",
    "process_societaire_demande",
    "rechercher_societaire",
    "scorer_demande",
]
