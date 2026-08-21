from solida.application.use_cases.lister_produits import ListerProduits
from solida.infrastructure.dependencies.adapters import grille_repository, lecteur


def lister_produits() -> ListerProduits:
    return ListerProduits(lecteur=lecteur(), grille_repository=grille_repository())
