from typing import Protocol

from solida.domain.values.decision import DecisionAEnregistrer, DecisionEnregistree


class DepotDecisions(Protocol):
    """`decision_scoring` est en insertion seule : ce port n'expose donc aucune
    méthode de modification ou de suppression, seulement l'écriture d'une
    nouvelle ligne et la lecture.
    """

    def enregistrer(self, decision: DecisionAEnregistrer) -> DecisionEnregistree: ...

    def lire(self, decision_id: str) -> DecisionEnregistree | None: ...

    def lister(
        self, agence_id: str | None, limite: int, decalage: int
    ) -> list[DecisionEnregistree]: ...

    def compter(self, agence_id: str | None) -> int: ...
