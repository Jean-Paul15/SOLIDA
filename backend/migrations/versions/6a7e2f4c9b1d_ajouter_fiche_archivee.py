"""ajouter fiche_archivee (metadonnees, PDF dans SeaweedFS)

Revision ID: 6a7e2f4c9b1d
Revises: 9d4a1f2b7c3e
Create Date: 2026-08-05 11:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "6a7e2f4c9b1d"
down_revision: str | None = "9d4a1f2b7c3e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fiche_archivee",
        sa.Column("fiche_id", sa.Uuid(), nullable=False),
        sa.Column("decision_id", sa.Uuid(), nullable=False),
        sa.Column("chemin_objet", sa.String(length=200), nullable=False),
        sa.Column("archive_par", sa.String(length=200), nullable=False),
        sa.Column(
            "archive_le", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["decision_id"], ["decision_scoring.decision_id"]),
        sa.PrimaryKeyConstraint("fiche_id"),
    )
    op.create_index(
        "ix_fiche_archivee_decision_id", "fiche_archivee", ["decision_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_fiche_archivee_decision_id", table_name="fiche_archivee")
    op.drop_table("fiche_archivee")
