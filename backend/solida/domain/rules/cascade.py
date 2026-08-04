from dataclasses import dataclass

from solida.domain.values.mode_calcul import ModeCalcul
from solida.domain.values.motif_bascule import MotifBascule


@dataclass(frozen=True)
class ContexteCascade:
    """Ce qu'il faut savoir sur le groupe d'un societaire pour choisir le modele.

    Le calcul des features elles-memes (regularite, historique du groupe...) est
    hors du domaine : cette regle ne fait que decider socle vs enrichi a partir
    d'un contexte deja calcule.
    """

    appartient_a_un_groupe: bool
    taille_groupe: int
    nb_credits_anterieurs_groupe_soldes: int
    fraicheur_features_jours: int | None


@dataclass(frozen=True)
class ParametresCascade:
    """Seuils d'eligibilite au mode enrichi. Ajustable par la cooperative."""

    taille_groupe_minimale: int = 3
    nb_credits_anterieurs_minimum: int = 3
    fraicheur_maximale_jours: int = 7


@dataclass(frozen=True)
class ResultatCascade:
    mode: ModeCalcul
    motif: MotifBascule | None = None


def determiner_mode(contexte: ContexteCascade, parametres: ParametresCascade) -> ResultatCascade:
    """Applique les quatre conditions du mode enrichi, dans l'ordre de leur dependance.

    On ne peut pas juger la taille d'un groupe auquel on n'appartient pas, ni son
    historique avant d'avoir verifie sa taille : l'ordre des verifications suit
    cette dependance logique, pas un choix arbitraire.
    """
    if not contexte.appartient_a_un_groupe:
        return ResultatCascade(mode=ModeCalcul.SOCLE_SEUL, motif=MotifBascule.SANS_GROUPE)

    if contexte.taille_groupe < parametres.taille_groupe_minimale:
        return ResultatCascade(mode=ModeCalcul.SOCLE_SEUL, motif=MotifBascule.GROUPE_TROP_PETIT)

    if contexte.nb_credits_anterieurs_groupe_soldes < parametres.nb_credits_anterieurs_minimum:
        return ResultatCascade(
            mode=ModeCalcul.SOCLE_SEUL, motif=MotifBascule.GROUPE_SANS_HISTORIQUE
        )

    fraicheur = contexte.fraicheur_features_jours
    if fraicheur is None or fraicheur >= parametres.fraicheur_maximale_jours:
        return ResultatCascade(mode=ModeCalcul.SOCLE_SEUL, motif=MotifBascule.FEATURES_PERIMEES)

    return ResultatCascade(mode=ModeCalcul.ENRICHI)
