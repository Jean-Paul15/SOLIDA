"""ajouter resultat_complementaire a decision_scoring

Revision ID: f7e6a07b7371
Revises: 316b99efb09e
Create Date: 2026-08-04 21:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f7e6a07b7371"
down_revision: str | None = "316b99efb09e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Porte ce que ResultatScoring expose au frontend mais qui n'a pas sa propre colonne
    # (motif_mode, points_de_base, plafond_progressif, trajectoire_progression,
    # conditions_reexamen, avertissements) : decision_scoring etant en insertion seule,
    # cette colonne doit permettre de reconstruire exactement la reponse d'origine, pas
    # de la recalculer a partir de donnees CORE-SIM qui peuvent avoir change depuis.
    op.add_column(
        "decision_scoring",
        sa.Column(
            "resultat_complementaire",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )


def downgrade() -> None:
    op.drop_column("decision_scoring", "resultat_complementaire")
