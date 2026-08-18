from datetime import date

from sqlalchemy import Engine, text

from solida.domain.entities.compte_epargne import CompteEpargne
from solida.domain.entities.mouvement_epargne import MouvementEpargne


class PostgresEpargneReader:
    def __init__(self, moteur: Engine) -> None:
        self._moteur = moteur

    def charger_compte_epargne(self, societaire_id: str) -> CompteEpargne | None:
        requete = text("""
            SELECT compte_id, societaire_id, solde_epargne_moyen_6m, nb_mois_avec_depot_12m,
                   croissance_epargne_12m, volatilite_epargne
            FROM comptes_epargne WHERE societaire_id = :id
        """)
        with self._moteur.connect() as connexion:
            ligne = connexion.execute(requete, {"id": societaire_id}).first()
        if ligne is None:
            return None
        return CompteEpargne(
            compte_id=ligne.compte_id,
            societaire_id=ligne.societaire_id,
            solde_moyen_6m=round(ligne.solde_epargne_moyen_6m),
            nb_mois_avec_depot_12m=ligne.nb_mois_avec_depot_12m,
            croissance_12m=float(ligne.croissance_epargne_12m),
            volatilite=float(ligne.volatilite_epargne),
        )

    def charger_mouvements_epargne(
        self, societaire_id: str, depuis: date
    ) -> list[MouvementEpargne]:
        requete = text("""
            SELECT m.mouvement_id, m.compte_id, m.date_operation, m.sens, m.montant
            FROM mouvements_epargne m
            JOIN comptes_epargne c ON c.compte_id = m.compte_id
            WHERE c.societaire_id = :id AND m.date_operation >= :depuis
            ORDER BY m.date_operation
        """)
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete, {"id": societaire_id, "depuis": depuis})
            return [
                MouvementEpargne(
                    mouvement_id=ligne.mouvement_id,
                    compte_id=ligne.compte_id,
                    date_operation=ligne.date_operation,
                    sens=ligne.sens,
                    montant=round(ligne.montant),
                )
                for ligne in lignes
            ]
