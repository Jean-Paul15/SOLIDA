import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from solida.adapters.persistence.orm_models.base import Base


class AuditEvent(Base):
    __tablename__ = "journal_audit"

    evenement_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(50), index=True)
    acteur_id: Mapped[str] = mapped_column(String(100))
    objet: Mapped[str] = mapped_column(String(200))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    horodatage: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    adresse_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
