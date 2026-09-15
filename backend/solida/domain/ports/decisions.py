from datetime import datetime
from typing import Protocol

from solida.domain.values.decision import DecisionAEnregistrer, DecisionEnregistree


class DecisionRepository(Protocol):
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

    def existe_decision_accordee_depuis(
        self, societaire_id: str, depuis: datetime, entree_actuelle: dict[str, object]
    ) -> bool:
        """Une décision `accord`/`accord_sous_condition` existe déjà pour ce sociétaire depuis
        `depuis` : signal de multi-octroi avant que CORE-SIM (système de vérité pour le
        décaissement, jamais écrit par SOLIDA) n'ait eu le temps de refléter le crédit résultant.
        `entree_actuelle` exclut la décision qui correspondrait à un simple retry de la même
        demande (double-clic, retry réseau) : ce cas reste couvert par la déduplication déjà en
        place dans `enregistrer`, pas par ce contrôle.
        """
        ...

    def dernier_agent_reel(self, societaire_id: str) -> str | None:
        """L'agent de la décision la plus récente déjà enregistrée pour ce sociétaire.
        `decision_scoring` ne contient que des décisions `confirm()`, jamais `preview()` (flux
        portail sociétaire) : le sentinel `AGENT_ID_PORTAIL` n'y apparaît donc jamais, aucun
        filtre applicatif n'est nécessaire. `None` si aucune décision antérieure n'existe — le
        sociétaire n'a alors pas d'agent habituel, et sa prochaine demande reste non assignée
        (le superviseur choisit)."""
        ...
