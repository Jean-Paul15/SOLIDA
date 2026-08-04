class ErreurSolida(Exception):
    """Racine commune à toutes les exceptions du domaine SOLIDA."""


class ErreurDomaine(ErreurSolida):
    """Violation d'une règle métier."""


class SocietaireIntrouvable(ErreurDomaine):
    """Aucun sociétaire ne correspond à l'identifiant fourni."""


class DonneesInsuffisantes(ErreurDomaine):
    """Les données disponibles ne permettent pas de calculer un score."""


class GrilleInvalide(ErreurDomaine):
    """Les paramètres de la grille de décision sont incohérents."""


class ModeleIndisponible(ErreurDomaine):
    """Aucun modèle de scoring (ni enrichi, ni socle) n'a pu produire une probabilité."""


class AccesRefuse(ErreurDomaine):
    """L'acteur courant n'a pas les droits nécessaires pour cette action."""


class InvariantScoreViole(ErreurDomaine):
    """La décomposition en points ne somme pas au score : le scoring est rejeté."""
