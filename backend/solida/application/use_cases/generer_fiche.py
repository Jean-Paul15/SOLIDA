from dataclasses import dataclass
from datetime import UTC, datetime

from solida.domain.ports.core_sim import LecteurCoreSim
from solida.domain.ports.decisions import DepotDecisions
from solida.domain.values.decision import DecisionEnregistree
from solida.domain.values.fiche import MENTION_LEGALE, EnTeteFiche


@dataclass(frozen=True)
class GenererFiche:
    depot_decisions: DepotDecisions
    lecteur: LecteurCoreSim

    def executer(self, decision_id: str) -> tuple[DecisionEnregistree, EnTeteFiche] | None:
        decision = self.depot_decisions.lire(decision_id)
        if decision is None:
            return None

        societaire = self.lecteur.charger_societaire(decision.societaire_id)
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
