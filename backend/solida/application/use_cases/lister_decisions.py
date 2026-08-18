from dataclasses import dataclass

from solida.domain.ports.core_sim import LecteurCoreSim
from solida.domain.ports.decisions import DecisionRepository
from solida.domain.values.decision import DecisionRegistreAffichee


@dataclass(frozen=True)
class ListerDecisions:
    decision_repository: DecisionRepository
    lecteur: LecteurCoreSim

    def executer(
        self, agence_id: str | None, limite: int, decalage: int
    ) -> tuple[list[DecisionRegistreAffichee], int]:
        decisions = self.decision_repository.lister(agence_id, limite, decalage)
        total = self.decision_repository.compter(agence_id)

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
            # `decision_repository.lister` filtre par l'agence de l'AGENT qui a note la decision
            # (seule donnee disponible cote SQL : CORE-SIM, qui porte l'agence du societaire,
            # est une base separee, jamais jointe). Les deux coincident normalement (un agent
            # ne peut scorer qu'un societaire de sa propre agence, voir scorer_demande.py),
            # mais une decision historique incoherente avec cette regle exposerait sinon un
            # autre societaire a un agent d'une autre agence : on revalide ici sur l'agence
            # reellement affichee, avec la donnee societaire de toute facon deja chargee pour
            # le nom.
            if agence_id is not None and agence != agence_id:
                continue
            affichees.append(
                DecisionRegistreAffichee(decision=decision, societaire_nom=nom, agence=agence)
            )

        return affichees, total
