from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from solida.adapters.persistence.orm_models.base import Base


class GrilleDecision(Base):
    __tablename__ = "grille_decision"

    version_grille: Mapped[str] = mapped_column(String(30), primary_key=True)
    seuils: Mapped[dict] = mapped_column(JSONB)
    pdo: Mapped[float] = mapped_column(Float)
    score_reference: Mapped[float] = mapped_column(Float)
    odds_reference: Mapped[float] = mapped_column(Float)
    date_activation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    auteur: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=False)
