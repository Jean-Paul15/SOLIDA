from solida.application.use_cases.archiver_fiche import ArchiverFiche
from solida.application.use_cases.generer_fiche import GenererFiche
from solida.application.use_cases.lire_decision import LireDecision
from solida.application.use_cases.scorer_demande import ScorerDemande
from solida.infrastructure.dependencies.adapters import (
    audit_log,
    core_sim_reader,
    decision_repository,
    feature_store,
    fiche_archivee_repository,
    fiche_pdf_generator,
    fiche_repository,
    grille_repository,
    scoring_model,
    scoring_model_enrichi,
)


def scorer_demande() -> ScorerDemande:
    return ScorerDemande(
        core_sim_reader=core_sim_reader(),
        feature_store=feature_store(),
        scoring_model=scoring_model(),
        scoring_model_enrichi=scoring_model_enrichi(),
        grille_repository=grille_repository(),
        decision_repository=decision_repository(),
        audit_log=audit_log(),
    )


def lire_decision() -> LireDecision:
    return LireDecision(decision_repository=decision_repository())


def generer_fiche() -> GenererFiche:
    return GenererFiche(
        decision_repository=decision_repository(), core_sim_reader=core_sim_reader()
    )


def archiver_fiche() -> ArchiverFiche:
    return ArchiverFiche(
        generer_fiche=generer_fiche(),
        fiche_pdf_generator=fiche_pdf_generator(),
        fiche_repository=fiche_repository(),
        fiche_archivee_repository=fiche_archivee_repository(),
        audit_log=audit_log(),
    )
