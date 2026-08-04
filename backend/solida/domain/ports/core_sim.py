from datetime import date
from typing import Protocol

from solida.domain.entities.compte_epargne import CompteEpargne
from solida.domain.entities.credit import Credit
from solida.domain.entities.garantie import Garantie
from solida.domain.entities.groupe import GroupeCaution
from solida.domain.entities.mouvement_epargne import MouvementEpargne
from solida.domain.entities.societaire import Societaire
from solida.domain.values.resultat_recherche import ResultatRechercheSocietaire


class LecteurCoreSim(Protocol):
    """Accès en lecture seule à CORE-SIM.

    Aucune implémentation de ce port n'écrit dans CORE-SIM : la garantie tient
    au rôle de base de données (`solida_lecteur`, `GRANT SELECT` uniquement),
    pas seulement à la discipline du code Python.
    """

    def rechercher_societaires(
        self, terme: str, limite: int, agence_id: str | None = None
    ) -> list[ResultatRechercheSocietaire]:
        """`agence_id` restreint la recherche à une agence : cloisonnement du rôle
        `agent`, appliqué dans la requête plutôt qu'en filtrant après coup pour ne
        pas perdre de résultats valides à cause de la limite.
        """
        ...

    def charger_societaire(self, societaire_id: str) -> Societaire | None: ...

    def charger_historique_credit(self, societaire_id: str) -> list[Credit]: ...

    def charger_compte_epargne(self, societaire_id: str) -> CompteEpargne | None: ...

    def charger_mouvements_epargne(
        self, societaire_id: str, depuis: date
    ) -> list[MouvementEpargne]: ...

    def charger_groupe(self, societaire_id: str) -> GroupeCaution | None: ...

    def charger_garanties(self, societaire_id: str) -> list[Garantie]: ...
