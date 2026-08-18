from typing import Protocol

from solida.domain.values.decision import DecisionEnregistree
from solida.domain.values.fiche import EnTeteFiche


class FichePdfGenerator(Protocol):
    def generer(self, decision: DecisionEnregistree, entete: EnTeteFiche) -> bytes: ...
