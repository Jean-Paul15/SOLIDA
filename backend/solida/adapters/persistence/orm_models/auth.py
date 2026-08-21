import uuid
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from solida.adapters.persistence.orm_models.base import Base

ROLES_VALIDES = ("agent", "superviseur", "auditeur", "administrateur")


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "utilisateur"

    identifiant: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    nom_complet: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20))
    agence_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    doit_changer_mot_de_passe: Mapped[bool] = mapped_column(Boolean, default=True)
    mot_de_passe_modifie_le: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    desactive_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    __tablename__ = "access_token"

    # Le mixin cible "user.id" en dur ; notre table utilisateur s'appelle "utilisateur".
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("utilisateur.id", ondelete="cascade"), nullable=False, index=True
    )
    derniere_activite_le: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
