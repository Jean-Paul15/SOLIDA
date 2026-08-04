from enum import StrEnum


class MotifBascule(StrEnum):
    """Motif interne de bascule vers le mode socle. Voir 03-MODELE/04-cascade-et-cold-start.md."""

    SANS_GROUPE = "sans_groupe"
    GROUPE_TROP_PETIT = "groupe_trop_petit"
    GROUPE_SANS_HISTORIQUE = "groupe_sans_historique"
    FEATURES_PERIMEES = "features_perimees"
