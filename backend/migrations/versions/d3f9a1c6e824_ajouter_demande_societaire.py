"""ajouter demande_societaire

Revision ID: d3f9a1c6e824
Revises: 47717ebe5930
Create Date: 2026-09-13 22:00:00.000000

"""

from collections.abc import Sequence

import fastapi_users_db_sqlalchemy.generics
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d3f9a1c6e824"
down_revision: str | None = "47717ebe5930"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Table separee de decision_scoring (insertion seule, reservee aux decisions
    # confirmees par un agent) : une demande soumise depuis le portail societaire est
    # une pre-verification, pas une decision de dossier -- donc mutable (statut,
    # archivage), jamais persistee dans decision_scoring.
    op.create_table(
        "demande_societaire",
        sa.Column("demande_id", sa.Uuid(), nullable=False),
        sa.Column("societaire_id", sa.String(length=50), nullable=False),
        sa.Column("agence_id", sa.String(length=20), nullable=False),
        sa.Column("montant_demande", sa.Integer(), nullable=False),
        sa.Column("objet_credit", sa.String(length=50), nullable=False),
        sa.Column("duree_mois", sa.Integer(), nullable=False),
        sa.Column("produit_id", sa.String(length=50), nullable=False),
        sa.Column("resultat", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False, server_default="nouvelle"),
        sa.Column(
            "assigne_a_agent_id", fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True
        ),
        sa.Column(
            "cree_le",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("archivee_le", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "archivee_par_agent_id", fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True
        ),
        sa.PrimaryKeyConstraint("demande_id"),
        sa.ForeignKeyConstraint(["assigne_a_agent_id"], ["utilisateur.id"]),
        sa.ForeignKeyConstraint(["archivee_par_agent_id"], ["utilisateur.id"]),
    )
    op.create_index(
        op.f("ix_demande_societaire_societaire_id"),
        "demande_societaire",
        ["societaire_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_demande_societaire_agence_id"),
        "demande_societaire",
        ["agence_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_demande_societaire_statut"), "demande_societaire", ["statut"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_demande_societaire_statut"), table_name="demande_societaire")
    op.drop_index(op.f("ix_demande_societaire_agence_id"), table_name="demande_societaire")
    op.drop_index(op.f("ix_demande_societaire_societaire_id"), table_name="demande_societaire")
    op.drop_table("demande_societaire")
