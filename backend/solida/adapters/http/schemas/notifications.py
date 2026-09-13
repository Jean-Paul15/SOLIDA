from pydantic import BaseModel

from solida.adapters.http.schemas.scoring import ScoringResult


class DemandeSocietaireNotification(BaseModel):
    demande_id: str
    societaire_id: str
    societaire_nom: str
    agence_id: str
    montant_demande: int
    objet_credit: str
    duree_mois: int
    produit_id: str
    resultat: ScoringResult
    statut: str
    cree_le: str
    assigne_a_agent_id: str | None


class PageNotifications(BaseModel):
    elements: list[DemandeSocietaireNotification]
    total: int
