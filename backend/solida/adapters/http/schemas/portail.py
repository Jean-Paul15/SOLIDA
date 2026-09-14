from pydantic import BaseModel, Field

from solida.adapters.http.schemas.scoring import ObjetCredit


class VerificationCompteRequete(BaseModel):
    numero_compte: str = Field(min_length=1)
    montant_dernier_depot: int = Field(ge=0)


class VerificationCompteReponse(BaseModel):
    jeton_session: str
    prenom: str


class DemandePreVerificationRequete(BaseModel):
    montant: int = Field(gt=0)
    objet: ObjetCredit
    duree_mois: int = Field(gt=0, le=1200)
    produit_id: str = Field(min_length=1)


class DemandePreVerificationReponse(BaseModel):
    issue: str
    message: str
    montant_propose: int | None = None
    demande_id: str
