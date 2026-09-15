from solida.adapters.http.mappers.commun import _decomposition_to_schema
from solida.adapters.http.mappers.scoring import decision_to_resultat_scoring
from solida.adapters.http.schemas import fiche as schema_fiche
from solida.adapters.http.schemas import scoring as schema_scoring
from solida.domain.values.decision import DecisionEnregistree
from solida.domain.values.fiche import EnTeteFiche

# Une fiche imprimée ne peut pas offrir un "afficher tout" interactif comme l'écran de score
# en direct (ContributionsChart.tsx) : on retient les facteurs de plus grand impact (la liste
# arrive déjà triée par |points| décroissant, cf. _decomposition_to_schema) et on chiffre le
# reste, plutôt que de noyer l'agent sous une vingtaine de lignes sur un document destiné à
# être lu vite, parfois devant le sociétaire.
NB_FACTEURS_MAX_FICHE = 4


def fiche_to_schema(
    decision: DecisionEnregistree, entete: EnTeteFiche
) -> schema_fiche.FicheJustification:
    contributions = _decomposition_to_schema(decision.decomposition, decision.features_utilisees)
    favorables = [c for c in contributions if c.sens == "favorable"]
    defavorables = [c for c in contributions if c.sens == "defavorable"]
    return schema_fiche.FicheJustification(
        fiche_id=decision.decision_id,
        resultat=decision_to_resultat_scoring(decision),
        demande=schema_scoring.ScoringInput(**decision.entree),
        societaire_nom=entete.societaire_nom,
        numero_membre=entete.numero_membre,
        agence=entete.agence,
        agent_nom=decision.agent_nom,
        date_edition=entete.date_edition.isoformat(),
        facteurs_favorables=favorables[:NB_FACTEURS_MAX_FICHE],
        facteurs_defavorables=defavorables[:NB_FACTEURS_MAX_FICHE],
        nb_facteurs_favorables_masques=max(0, len(favorables) - NB_FACTEURS_MAX_FICHE),
        nb_facteurs_defavorables_masques=max(0, len(defavorables) - NB_FACTEURS_MAX_FICHE),
        conditions_reexamen=decision.conditions_reexamen,
        mention_legale=entete.mention_legale,
    )
