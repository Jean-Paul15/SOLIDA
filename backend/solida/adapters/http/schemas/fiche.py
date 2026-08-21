from pydantic import BaseModel

from solida.adapters.http.schemas.scoring import (
    ContributionVariable,
    ScoringInput,
    ScoringResult,
)


class FicheJustification(BaseModel):
    fiche_id: str
    resultat: ScoringResult
    demande: ScoringInput
    societaire_nom: str
    numero_membre: str
    agence: str
    agent_nom: str
    date_edition: str
    facteurs_favorables: list[ContributionVariable]
    facteurs_defavorables: list[ContributionVariable]
    conditions_reexamen: list[str]
    mention_legale: str
