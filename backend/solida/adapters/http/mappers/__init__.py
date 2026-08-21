"""Conversion des value objects du domaine vers les schémas pydantic exposés en HTTP.

Un module par sous-domaine (scoring, registre, société/dossier, fiche, grille, produit) ;
`__init__.py` réexporte les fonctions publiques pour que les routers et
`adapters/pdf/fiche_pdf_generator_weasyprint.py` continuent d'écrire `mappers.xxx_to_schema`
sans connaître ce découpage interne.
"""

from solida.adapters.http.mappers.fiche import fiche_to_schema
from solida.adapters.http.mappers.grille import grille_to_schema
from solida.adapters.http.mappers.produit import produit_to_schema
from solida.adapters.http.mappers.registre import decision_to_registre
from solida.adapters.http.mappers.scoring import (
    decision_a_enregistrer_to_resultat_scoring,
    decision_to_resultat_scoring,
)
from solida.adapters.http.mappers.societaire import dossier_to_schema, groupe_to_schema

__all__ = [
    "decision_a_enregistrer_to_resultat_scoring",
    "decision_to_registre",
    "decision_to_resultat_scoring",
    "dossier_to_schema",
    "fiche_to_schema",
    "grille_to_schema",
    "groupe_to_schema",
    "produit_to_schema",
]
