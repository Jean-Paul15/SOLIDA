from dataclasses import dataclass
from datetime import UTC, datetime

from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.ports.decisions import DecisionRepository
from solida.domain.values.decision import DecisionEnregistree
from solida.domain.values.fiche import MENTION_LEGALE, EnTeteFiche


@dataclass(frozen=True)
class GenererFiche:
    decision_repository: DecisionRepository
    core_sim_reader: CoreSimReader

    def execute(self, decision_id: str) -> tuple[DecisionEnregistree, EnTeteFiche] | None:
        decision = self.decision_repository.lire(decision_id)
        if decision is None:
            return None

        societaire = self.core_sim_reader.charger_societaire(decision.societaire_id)
        if societaire is None:
            return None

        entete = EnTeteFiche(
            societaire_nom=societaire.nom_complet,
            numero_membre=societaire.numero_membre,
            agence=societaire.agence,
            date_edition=datetime.now(UTC),
            mention_legale=MENTION_LEGALE,
        )
        return decision, entete
