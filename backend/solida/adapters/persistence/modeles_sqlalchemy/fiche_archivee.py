import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from solida.adapters.persistence.modeles_sqlalchemy.base import Base


class FicheArchivee(Base):
    """Métadonnées seulement — le PDF lui-même vit dans le stockage objet (SeaweedFS),
    jamais en base, pour ne pas alourdir `solida` d'un contenu binaire volumineux."""

    __tablename__ = "fiche_archivee"

    fiche_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    decision_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("decision_scoring.decision_id"), index=True
    )
    chemin_objet: Mapped[str] = mapped_column(String(200))
    archive_par: Mapped[str] = mapped_column(String(200))
    archive_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
