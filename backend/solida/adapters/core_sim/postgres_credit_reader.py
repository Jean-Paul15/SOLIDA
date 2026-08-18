from datetime import date
from typing import Any

from sqlalchemy import Engine, text

from solida.domain.entities.credit import Credit


def _capital_restant_du(
    montant_octroye: int, statut: str, date_deblocage: date, duree_mois: int, aujourdhui: date
) -> int:
    """Approxime le capital restant dû.

    Le générateur produit des crédits bruts (montant, durée, statut) mais pas
    d'échéancier de remboursement détaillé : cette fonction est une estimation
    d'affichage, documentée comme telle, pas un calcul comptable exact.

    `solde` : intégralement remboursé, 0. `en_souffrance` : aucune donnée de
    remboursement partiel n'existe dans le générateur, donc le montant octroyé
    est traité comme intégralement impayé plutôt que d'appliquer un
    amortissement qui suppose, à tort, un remboursement en cours. `en_cours` :
    amortissement linéaire sur la durée écoulée, seule approximation
    raisonnable pour un crédit dont l'issue n'est pas encore connue.
    """
    if statut == "solde":
        return 0
    if statut == "en_souffrance":
        return montant_octroye
    mois_ecoules = max(
        0, (aujourdhui.year - date_deblocage.year) * 12 + aujourdhui.month - date_deblocage.month
    )
    fraction_restante = max(0.0, 1.0 - min(mois_ecoules, duree_mois) / duree_mois)
    return round(montant_octroye * fraction_restante)


def _ligne_vers_credit(ligne: Any, aujourdhui: date) -> Credit:
    date_deblocage: date = ligne.date_deblocage
    duree_mois: int = ligne.duree_mois
    statut: str = ligne.statut
    return Credit(
        credit_id=ligne.credit_id,
        societaire_id=ligne.societaire_id,
        produit_id=ligne.produit_id,
        date_deblocage=date_deblocage,
        date_echeance_prevue=ligne.date_issue,
        duree_mois=duree_mois,
        numero_cycle=ligne.numero_cycle,
        montant_octroye=ligne.montant_octroye,
        statut=statut,
        jours_retard_max=(
            None if ligne.jours_retard_max is None else round(ligne.jours_retard_max)
        ),
        capital_restant_du=_capital_restant_du(
            ligne.montant_octroye, statut, date_deblocage, duree_mois, aujourdhui
        ),
    )


class PostgresCreditReader:
    def __init__(self, moteur: Engine) -> None:
        self._moteur = moteur

    def charger_historique_credit(self, societaire_id: str) -> list[Credit]:
        requete = text("""
            SELECT credit_id, societaire_id, produit_id, date_deblocage, date_issue, duree_mois,
                   numero_cycle, montant_octroye, statut, jours_retard_max
            FROM credits WHERE societaire_id = :id ORDER BY date_deblocage DESC
        """)
        aujourdhui = date.today()
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete, {"id": societaire_id})
            return [_ligne_vers_credit(ligne, aujourdhui) for ligne in lignes]
