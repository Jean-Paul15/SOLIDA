from pydantic import BaseModel

from solida.adapters.http.schemas.scoring import EntreeScoring, ResultatScoring


class DecisionRegistre(BaseModel):
    decision_id: str
    societaire_id: str
    societaire_nom: str
    agence: str
    demande: EntreeScoring
    resultat: ResultatScoring
    horodatage: str
    agent_nom: str


class PageRegistre(BaseModel):
    elements: list[DecisionRegistre]
    total: int
