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
    # Le sociétaire ne choisit plus de produit (étape retirée du parcours) : `ProcessSocietaireDemande`
    # le déduit du segment du sociétaire. Conservé optionnel pour ne pas casser un appel qui le
    # fournirait encore (file hors-ligne déjà en attente sur un téléphone, par ex.).
    produit_id: str | None = Field(default=None, min_length=1)
    # Optionnels : le sociétaire peut ne pas connaître ces montants précisément. Mêmes champs
    # que l'actualisation déjà collectée côté agent (RefreshFields.tsx) — jamais consommés tels
    # quels si absents, le modèle traite alors l'information comme manquante (pas comme zéro).
    revenu_mensuel_declare: int | None = Field(default=None, ge=0)
    charges_mensuelles: int | None = Field(default=None, ge=0)


class DemandePreVerificationReponse(BaseModel):
    issue: str
    message: str
    montant_propose: int | None = None
    demande_id: str
