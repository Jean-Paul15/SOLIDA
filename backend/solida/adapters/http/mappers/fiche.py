from solida.adapters.http.mappers.commun import _decomposition_to_schema
from solida.adapters.http.mappers.scoring import decision_to_resultat_scoring
from solida.adapters.http.schemas import fiche as schema_fiche
from solida.adapters.http.schemas import scoring as schema_scoring
from solida.domain.values.decision import DecisionEnregistree
from solida.domain.values.fiche import EnTeteFiche


def fiche_to_schema(
    decision: DecisionEnregistree, entete: EnTeteFiche
) -> schema_fiche.FicheJustification:
    contributions = _decomposition_to_schema(decision.decomposition, decision.features_utilisees)
    return schema_fiche.FicheJustification(
        fiche_id=decision.decision_id,
        resultat=decision_to_resultat_scoring(decision),
        demande=schema_scoring.ScoringInput(**decision.entree),
        societaire_nom=entete.societaire_nom,
        numero_membre=entete.numero_membre,
        agence=entete.agence,
        agent_nom=decision.agent_nom,
        date_edition=entete.date_edition.isoformat(),
        facteurs_favorables=[c for c in contributions if c.sens == "favorable"],
        facteurs_defavorables=[c for c in contributions if c.sens == "defavorable"],
        conditions_reexamen=decision.conditions_reexamen,
        mention_legale=entete.mention_legale,
    )
