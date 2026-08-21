from pydantic import BaseModel

from solida.adapters.http.schemas.scoring import ScoringInput, ScoringResult


class DecisionRegistre(BaseModel):
    decision_id: str
    societaire_id: str
    societaire_nom: str
    agence: str
    demande: ScoringInput
    resultat: ScoringResult
    horodatage: str
    agent_nom: str


class PageRegistre(BaseModel):
    elements: list[DecisionRegistre]
    total: int
