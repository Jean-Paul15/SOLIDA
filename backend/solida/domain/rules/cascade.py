from dataclasses import dataclass

from solida.domain.values.mode_calcul import ModeCalcul
from solida.domain.values.motif_bascule import MotifBascule


@dataclass(frozen=True)
class ContexteCascade:
    """Ce qu'il faut savoir sur le groupe d'un sociétaire pour choisir le modèle.

    Le calcul des features elles-mêmes (régularité, historique du groupe...) est
    hors du domaine : cette règle ne fait que décider socle vs enrichi à partir
    d'un contexte déjà calculé.
    """

    appartient_a_un_groupe: bool
    taille_groupe: int
    nb_credits_anterieurs_groupe_soldes: int
    fraicheur_features_jours: int | None


@dataclass(frozen=True)
class ParametresCascade:
    """Seuils d'éligibilité au mode enrichi. Ajustable par la coopérative."""

    taille_groupe_minimale: int = 5
    """Seuil terrain (`précision.txt` réponse 22) : un groupe n'est jugeable qu'à partir de
    5 membres actifs. Aligné sur `SEUIL_TAILLE_GROUPE_JUGEABLE` (modelisation.catalogue),
    utilisé côté entraînement pour la même raison."""
    nb_credits_anterieurs_minimum: int = 3
    fraicheur_maximale_jours: int = 7


@dataclass(frozen=True)
class ResultatCascade:
    mode: ModeCalcul
    motif: MotifBascule | None = None


def determiner_mode(contexte: ContexteCascade, parametres: ParametresCascade) -> ResultatCascade:
    """Applique les quatre conditions du mode enrichi, dans l'ordre de leur dépendance.

    On ne peut pas juger la taille d'un groupe auquel on n'appartient pas, ni son
    historique avant d'avoir vérifié sa taille : l'ordre des vérifications suit
    cette dépendance logique, pas un choix arbitraire.
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
