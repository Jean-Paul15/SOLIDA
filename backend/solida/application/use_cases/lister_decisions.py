from dataclasses import dataclass

from solida.domain.ports.core_sim import LecteurCoreSim
from solida.domain.ports.decisions import DepotDecisions
from solida.domain.values.decision import DecisionRegistreAffichee


@dataclass(frozen=True)
class ListerDecisions:
    depot: DepotDecisions
    lecteur: LecteurCoreSim

    def executer(
        self, agence_id: str | None, limite: int, decalage: int
    ) -> tuple[list[DecisionRegistreAffichee], int]:
        decisions = self.depot.lister(agence_id, limite, decalage)
        total = self.depot.compter(agence_id)

        noms_par_societaire: dict[str, tuple[str, str]] = {}
        affichees = []
        for decision in decisions:
            if decision.societaire_id not in noms_par_societaire:
                societaire = self.lecteur.charger_societaire(decision.societaire_id)
                noms_par_societaire[decision.societaire_id] = (
                    (societaire.nom_complet, societaire.agence)
                    if societaire is not None
                    else ("Sociétaire introuvable", "")
                )
            nom, agence = noms_par_societaire[decision.societaire_id]
            affichees.append(
                DecisionRegistreAffichee(decision=decision, societaire_nom=nom, agence=agence)
            )

        return affichees, total
