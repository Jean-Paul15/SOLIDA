from enum import StrEnum


class MotifBascule(StrEnum):
    """Motif interne de bascule vers le mode socle."""

    SANS_GROUPE = "sans_groupe"
    GROUPE_TROP_PETIT = "groupe_trop_petit"
    GROUPE_SANS_HISTORIQUE = "groupe_sans_historique"
    FEATURES_PERIMEES = "features_perimees"
