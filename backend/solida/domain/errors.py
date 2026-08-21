class SolidaError(Exception):
    """Racine commune à toutes les exceptions du domaine SOLIDA."""


class DomainError(SolidaError):
    """Violation d'une règle métier."""


class SocietaireIntrouvable(DomainError):
    """Aucun sociétaire ne correspond à l'identifiant fourni."""


class DonneesInsuffisantes(DomainError):
    """Les données disponibles ne permettent pas de calculer un score."""


class GrilleInvalide(DomainError):
    """Les paramètres de la grille de décision sont incohérents."""


class ModeleIndisponible(DomainError):
    """Aucun modèle de scoring (ni enrichi, ni socle) n'a pu produire une probabilité."""


class AccesRefuse(DomainError):
    """L'acteur courant n'a pas les droits nécessaires pour cette action."""


class InvariantScoreViole(DomainError):
    """La décomposition en points ne somme pas au score : le scoring est rejeté."""


class MotDePasseInvalide(DomainError):
    """Le mot de passe proposé ne respecte pas la politique en vigueur."""


class MontantDemandeInvalide(DomainError):
    """Le montant demandé dépasse le plafond produit de la grille active."""


class DureeDemandeeInvalide(DomainError):
    """La durée demandée sort des bornes du produit de crédit choisi."""


class ProduitIntrouvable(DomainError):
    """Aucun produit de crédit ne correspond à l'identifiant fourni."""


class SurEndettement(DomainError):
    """Le sociétaire a déjà un crédit en cours : refus d'un nouvel octroi par ce canal."""


class VersionGrilleDejaExistante(DomainError):
    """Une configuration de grille porte déjà ce `version_grille`."""


class ScorecardImmuable(DomainError):
    """pdo/score_reference/odds_reference ne se modifient plus par ce canal (calibration en
    attente du modèle réel, cf. docs/backend/03-decisions-provisoires-a-revoir.md)."""
