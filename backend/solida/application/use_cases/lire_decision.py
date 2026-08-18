from dataclasses import dataclass

from solida.domain.ports.decisions import DecisionRepository
from solida.domain.values.decision import DecisionEnregistree


@dataclass(frozen=True)
class LireDecision:
    decision_repository: DecisionRepository

    def executer(self, decision_id: str) -> DecisionEnregistree | None:
        return self.decision_repository.lire(decision_id)
