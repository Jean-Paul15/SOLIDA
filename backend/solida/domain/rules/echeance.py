import math

# Le TAEG plafond BCEAO pour les SFD est de 24 % l'an (UEMOA, depuis le 1er juin 2026).
# Cette valeur est un taux de démonstration, largement sous le plafond, en l'absence
# d'une table de taux par produit de crédit : à remplacer dès qu'elle existe.
TAUX_MENSUEL_DEMONSTRATION = 0.18 / 12


def calculer_echeance_mensuelle(
    montant_demande: float, duree_mois: int, taux_mensuel: float
) -> int:
    """Amortissement à annuité constante (méthode actuarielle) : c'est la méthode que la
    réglementation BCEAO impose pour exprimer le TEG/TAEG des crédits dans l'UEMOA, et celle
    qu'appliquent en pratique les coopératives d'épargne et de crédit togolaises (intérêt
    dégressif sur le capital restant dû, pas un taux forfaitaire sur le montant initial).

    echeance = montant * [i * (1+i)^n] / [(1+i)^n - 1], où i est le taux mensuel.
    """
    if duree_mois <= 0:
        return 0
    if taux_mensuel == 0:
        return round(montant_demande / duree_mois)

    facteur = math.pow(1 + taux_mensuel, duree_mois)
    return round((montant_demande * taux_mensuel * facteur) / (facteur - 1))


def calculer_taux_endettement(
    charges_mensuelles: float, revenu_mensuel: float, echeance_mensuelle: float
) -> float:
    if revenu_mensuel <= 0:
        return 0.0
    return (charges_mensuelles + echeance_mensuelle) / revenu_mensuel
