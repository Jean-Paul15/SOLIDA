from solida.adapters.http.mappers.scoring import decision_vers_resultat_scoring
from solida.adapters.http.schemas import registre as schema_registre
from solida.adapters.http.schemas import scoring as schema_scoring
from solida.domain.values.decision import DecisionRegistreAffichee


def decision_vers_registre(
    affichee: DecisionRegistreAffichee,
) -> schema_registre.DecisionRegistre:
    decision = affichee.decision
    return schema_registre.DecisionRegistre(
        decision_id=decision.decision_id,
        societaire_id=decision.societaire_id,
        societaire_nom=affichee.societaire_nom,
        agence=affichee.agence,
        demande=schema_scoring.EntreeScoring(**decision.entree),
        resultat=decision_vers_resultat_scoring(decision),
        horodatage=decision.horodatage.isoformat(),
        agent_nom=decision.agent_nom,
    )
