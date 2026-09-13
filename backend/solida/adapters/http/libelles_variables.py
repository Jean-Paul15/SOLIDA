"""Traduction des codes de variables du modèle vers ce qu'un agent doit lire à l'écran.

Le domaine ne connaît que des codes techniques (`ratio_endettement`, `en_groupe`, ...) —
cette couche de présentation leur associe un libellé, une famille d'affichage et un format
de valeur, à partir des seules données réellement produites par le calcul (aucune valeur
inventée : la valeur affichée est toujours celle qui a servi au calcul du score).
"""

from typing import Literal

Famille = Literal["profil", "activite", "epargne", "historique", "solidaire", "demande"]


class _Definition:
    __slots__ = ("libelle", "famille", "format")

    def __init__(self, libelle: str, famille: Famille, format: str) -> None:
        self.libelle = libelle
        self.famille = famille
        self.format = format


_DEFINITIONS: dict[str, _Definition] = {
    "anciennete_societaire_mois": _Definition(
        "Ancienneté en tant que sociétaire", "profil", "mois"
    ),
    "zone_residence": _Definition("Zone de résidence", "profil", "texte"),
    "revenu_mensuel_declare": _Definition("Revenu mensuel déclaré", "profil", "fcfa"),
    "duree_demandee_mois": _Definition("Durée demandée", "demande", "mois"),
    "solde_epargne_moyen_6m": _Definition("Solde d'épargne moyen (6 mois)", "epargne", "fcfa"),
    "nb_mois_avec_depot_12m": _Definition(
        "Régularité des dépôts (12 mois)", "epargne", "mois_sur_12"
    ),
    "volatilite_epargne": _Definition("Volatilité de l'épargne", "epargne", "pourcentage"),
    "ratio_epargne_revenu": _Definition("Épargne rapportée au revenu", "epargne", "pourcentage"),
    "ratio_epargne_montant": _Definition(
        "Épargne rapportée au montant demandé", "demande", "pourcentage"
    ),
    "anciennete_epargne_mois": _Definition(
        "Ancienneté de la relation d'épargne", "epargne", "mois"
    ),
    "ratio_endettement": _Definition("Taux d'endettement résultant", "demande", "pourcentage"),
    "nb_credits_anterieurs": _Definition("Crédits antérieurs", "historique", "entier"),
    "nb_incidents_anterieurs": _Definition(
        "Incidents de remboursement antérieurs", "historique", "entier"
    ),
    "max_jours_retard_historique": _Definition("Retard maximal observé", "historique", "jours"),
    "montant_max_rembourse": _Definition("Plus gros montant déjà remboursé", "historique", "fcfa"),
    "numero_cycle": _Definition("Cycle de crédit", "historique", "entier"),
    "ratio_montant_historique": _Definition(
        "Montant demandé rapporté au meilleur remboursement", "demande", "pourcentage"
    ),
    "parts_sociales_montant": _Definition("Montant des parts sociales", "profil", "fcfa"),
    "nb_personnes_a_charge": _Definition("Personnes à charge", "profil", "entier"),
    "en_groupe": _Definition("Appartenance à un groupe de caution", "solidaire", "booleen"),
}

_DEFINITION_INCONNUE = _Definition("Variable non documentée", "profil", "brut")


def libelle(code_variable: str) -> str:
    return _DEFINITIONS.get(code_variable, _DEFINITION_INCONNUE).libelle


def famille(code_variable: str) -> Famille:
    return _DEFINITIONS.get(code_variable, _DEFINITION_INCONNUE).famille


def formater_valeur(code_variable: str, valeur: float | int | str | bool | None) -> str:
    if valeur is None:
        return "Non renseigné"
    format_ = _DEFINITIONS.get(code_variable, _DEFINITION_INCONNUE).format
    if format_ in {"texte", "brut"}:
        return str(valeur)
    if format_ == "booleen":
        return "Oui" if bool(valeur) else "Non"
    if not isinstance(valeur, (float, int)):
        return str(valeur)
    if format_ == "fcfa":
        return f"{int(valeur):,} FCFA".replace(",", " ")
    if format_ == "pourcentage":
        return f"{valeur * 100:.0f} %"
    if format_ == "mois":
        return f"{int(valeur)} mois"
    if format_ == "mois_sur_12":
        return f"{int(valeur)}/12 mois"
    if format_ == "jours":
        return f"{int(valeur)} jours"
    if format_ == "entier":
        return str(int(valeur))
    return str(valeur)


def sens(points: float) -> Literal["favorable", "defavorable", "neutre"]:
    if points > 0:
        return "favorable"
    if points < 0:
        return "defavorable"
    return "neutre"


def explication(code_variable: str, valeur_affichee: str, points: float) -> str:
    jugement = {
        "favorable": "contribue positivement au score",
        "defavorable": "pèse négativement sur le score",
        "neutre": "n'a pas d'effet notable sur le score",
    }[sens(points)]
    return f"{libelle(code_variable)} : {valeur_affichee} ; {jugement}."
