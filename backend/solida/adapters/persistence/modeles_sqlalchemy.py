import uuid
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


ROLES_VALIDES = ("agent", "superviseur", "auditeur", "administrateur")


class Utilisateur(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "utilisateur"

    identifiant: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    nom_complet: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20))
    agence_id: Mapped[str | None] = mapped_column(String(20), nullable=True)


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    __tablename__ = "access_token"

    # Le mixin cible "user.id" en dur ; notre table utilisateur s'appelle "utilisateur".
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("utilisateur.id", ondelete="cascade"), nullable=False
    )


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
    horodatage: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class JournalAudit(Base):
    __tablename__ = "journal_audit"

    evenement_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(50), index=True)
    acteur_id: Mapped[str] = mapped_column(String(100))
    objet: Mapped[str] = mapped_column(String(200))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    horodatage: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    adresse_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
