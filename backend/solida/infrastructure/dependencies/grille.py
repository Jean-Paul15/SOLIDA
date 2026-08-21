from solida.application.use_cases.gerer_grille import LireGrilleActive, ModifierGrille
from solida.infrastructure.dependencies.adapters import grille_repository


def lire_grille_active() -> LireGrilleActive:
    return LireGrilleActive(grille_repository=grille_repository())


def modifier_grille() -> ModifierGrille:
    return ModifierGrille(grille_repository=grille_repository())
