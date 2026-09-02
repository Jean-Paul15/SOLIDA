from dataclasses import dataclass

from solida.domain.ports.core_sim import CoreSimReader
from solida.domain.ports.decisions import DecisionRepository
from solida.domain.values.decision import DecisionRegistreAffichee


@dataclass(frozen=True)
class ListerDecisions:
    decision_repository: DecisionRepository
    core_sim_reader: CoreSimReader

    def execute(
        self, agence_id: str | None, limite: int, decalage: int
    ) -> tuple[list[DecisionRegistreAffichee], int]:
        decisions = self.decision_repository.lister(agence_id, limite, decalage)
        total = self.decision_repository.compter(agence_id)

        noms_par_societaire: dict[str, tuple[str, str]] = {}
        affichees = []
        for decision in decisions:
            if decision.societaire_id not in noms_par_societaire:
                societaire = self.core_sim_reader.charger_societaire(decision.societaire_id)
                noms_par_societaire[decision.societaire_id] = (
                    (societaire.nom_complet, societaire.agence)
                    if societaire is not None
                    else ("Sociétaire introuvable", "")
                )
            nom, agence = noms_par_societaire[decision.societaire_id]
            # La requête SQL filtre l'agence de l'agent ; CORE-SIM porte celle du sociétaire.
            # Revalider évite qu'une décision historique incohérente expose un autre dossier.
            if agence_id is not None and agence != agence_id:
                continue
            affichees.append(
                DecisionRegistreAffichee(decision=decision, societaire_nom=nom, agence=agence)
            )

        return affichees, total
