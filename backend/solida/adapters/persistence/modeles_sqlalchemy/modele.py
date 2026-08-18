from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from solida.adapters.persistence.modeles_sqlalchemy.base import Base


class Modele(Base):
    __tablename__ = "modele"

    modele_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    type: Mapped[str] = mapped_column(String(20))
    version: Mapped[str] = mapped_column(String(30))
    chemin_artefact: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metriques: Mapped[dict] = mapped_column(JSONB, default=dict)
    date_entrainement: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actif: Mapped[bool] = mapped_column(Boolean, default=False)
