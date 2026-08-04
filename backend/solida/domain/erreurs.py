class ErreurSolida(Exception):
    """Racine commune a toutes les exceptions du domaine SOLIDA."""


class ErreurDomaine(ErreurSolida):
    """Violation d'une regle metier."""


class SocietaireIntrouvable(ErreurDomaine):
    """Aucun societaire ne correspond a l'identifiant fourni."""


class DonneesInsuffisantes(ErreurDomaine):
    """Les donnees disponibles ne permettent pas de calculer un score."""


class GrilleInvalide(ErreurDomaine):
    """Les parametres de la grille de decision sont incoherents."""


class ModeleIndisponible(ErreurDomaine):
    """Aucun modele de scoring (ni enrichi, ni socle) n'a pu produire une probabilite."""


class AccesRefuse(ErreurDomaine):
    """L'acteur courant n'a pas les droits necessaires pour cette action."""


class InvariantScoreViole(ErreurDomaine):
    """La decomposition en points ne somme pas au score : le scoring est rejete."""
