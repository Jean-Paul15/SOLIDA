from dataclasses import dataclass

from solida.domain.ports.decisions import DepotDecisions
from solida.domain.values.decision import DecisionEnregistree


@dataclass(frozen=True)
class LireDecision:
    depot: DepotDecisions

    def executer(self, decision_id: str) -> DecisionEnregistree | None:
        return self.depot.lire(decision_id)
