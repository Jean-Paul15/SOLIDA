from solida.domain.errors import MotDePasseInvalide

LONGUEUR_MINIMALE = 8
"""NIST SP 800-63B rev.4 : 8 caractères est le plancher SHALL, quel que soit le nombre de
facteurs — 15 n'est qu'une recommandation SHOULD renforcée en l'absence de second facteur.
Choix produit : 8, pour rester praticable pour des agents de coopérative sans MFA."""

LONGUEUR_MAXIMALE = 64


def valider_mot_de_passe(mot_de_passe: str, mots_de_passe_courants: frozenset[str]) -> None:
    """Lève `MotDePasseInvalide` si une règle est violée ; ne renvoie rien sinon.

    Aucune règle de composition (majuscule/chiffre/symbole) : NIST SP 800-63B rev.4
    l'interdit explicitement, ces règles poussent vers des mots de passe prévisibles.
    """
    if len(mot_de_passe) < LONGUEUR_MINIMALE:
        raise MotDePasseInvalide(
            f"Le mot de passe doit contenir au moins {LONGUEUR_MINIMALE} caractères."
        )
    if len(mot_de_passe) > LONGUEUR_MAXIMALE:
        raise MotDePasseInvalide(
            f"Le mot de passe ne peut pas dépasser {LONGUEUR_MAXIMALE} caractères."
        )
    if mot_de_passe.lower() in mots_de_passe_courants:
        raise MotDePasseInvalide("Ce mot de passe est trop courant, choisissez-en un autre.")
