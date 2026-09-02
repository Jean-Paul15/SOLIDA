from solida.application.use_cases.lister_produits import ListerProduits
from solida.infrastructure.dependencies.adapters import core_sim_reader, grille_repository


def lister_produits() -> ListerProduits:
    return ListerProduits(core_sim_reader=core_sim_reader(), grille_repository=grille_repository())
