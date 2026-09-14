from solida_modelisation.finance import mensualite_actuarielle

from solida.domain.values.montant import Montant


def montant_maximal_supportable(
    revenu_mensuel: int, duree_mois: int, taux_annuel: float, ratio_endettement_maximal: float
) -> Montant:
    """Plus grand montant dont la mensualité actuarielle ne dépasse pas
    `ratio_endettement_maximal` du revenu mensuel déclaré.

    Réutilise `mensualite_actuarielle` (partagée avec `modelisation`) sur un montant
    unitaire : la mensualité étant linéaire au montant emprunté à durée et taux fixés,
    diviser la mensualité maximale tolérée par cette mensualité unitaire donne directement
    le montant maximal, sans dupliquer la formule d'amortissement.
    """
    mensualite_maximale = revenu_mensuel * ratio_endettement_maximal
    mensualite_unitaire = mensualite_actuarielle(1.0, duree_mois, taux_annuel)
    if mensualite_unitaire <= 0:
        return Montant(valeur=0)
    return Montant(valeur=max(0, round(mensualite_maximale / mensualite_unitaire)))
