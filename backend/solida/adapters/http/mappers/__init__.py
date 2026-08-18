"""Conversion des value objects du domaine vers les schémas pydantic exposés en HTTP.

Un module par sous-domaine (scoring, registre, société/dossier, fiche, grille, produit) ;
`__init__.py` réexporte les fonctions publiques pour que les routeurs et
`adapters/pdf/fiche_pdf_generator_weasyprint.py` continuent d'écrire `mappers.xxx_vers_schema`
sans connaître ce découpage interne.
"""

from solida.adapters.http.mappers.fiche import fiche_vers_schema
from solida.adapters.http.mappers.grille import grille_vers_schema
from solida.adapters.http.mappers.produit import produit_vers_schema
from solida.adapters.http.mappers.registre import decision_vers_registre
from solida.adapters.http.mappers.scoring import (
    decision_a_enregistrer_vers_resultat_scoring,
    decision_vers_resultat_scoring,
)
from solida.adapters.http.mappers.societaire import dossier_vers_schema, groupe_vers_schema

__all__ = [
    "decision_a_enregistrer_vers_resultat_scoring",
    "decision_vers_registre",
    "decision_vers_resultat_scoring",
    "dossier_vers_schema",
    "fiche_vers_schema",
    "grille_vers_schema",
    "groupe_vers_schema",
    "produit_vers_schema",
]
