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


class MotDePasseInvalide(ErreurDomaine):
    """Le mot de passe proposé ne respecte pas la politique en vigueur."""


class MontantDemandeInvalide(ErreurDomaine):
    """Le montant demandé dépasse le plafond produit de la grille active."""


class DureeDemandeeInvalide(ErreurDomaine):
    """La durée demandée sort des bornes du produit de crédit choisi."""


class ProduitIntrouvable(ErreurDomaine):
    """Aucun produit de crédit ne correspond à l'identifiant fourni."""


class SurEndettement(ErreurDomaine):
    """Le sociétaire a déjà un crédit en cours : refus d'un nouvel octroi par ce canal."""


class VersionGrilleDejaExistante(ErreurDomaine):
    """Une configuration de grille porte déjà ce `version_grille`."""
