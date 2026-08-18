import uuid
from datetime import datetime

from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from solida.adapters.persistence.modeles_sqlalchemy.base import Base


class DecisionScoring(Base):
    __tablename__ = "decision_scoring"

    decision_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    societaire_id: Mapped[str] = mapped_column(String(50), index=True)
    agent_id: Mapped[uuid.UUID] = mapped_column(GUID, ForeignKey("utilisateur.id"))
    entree: Mapped[dict] = mapped_column(JSONB)
    features_utilisees: Mapped[dict] = mapped_column(JSONB)
    probabilite: Mapped[float] = mapped_column(Float)
    score: Mapped[float] = mapped_column(Float)
    tranche: Mapped[str] = mapped_column(String(30))
    montant_recommande: Mapped[int] = mapped_column(Integer)
    mode_calcul: Mapped[str] = mapped_column(String(20))
    decomposition: Mapped[dict] = mapped_column(JSONB)
    resultat_complementaire: Mapped[dict] = mapped_column(JSONB, default=dict)
    version_modele: Mapped[str] = mapped_column(String(30))
    version_grille: Mapped[str] = mapped_column(String(30))
    horodatage: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
