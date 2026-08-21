"""plafonds par produit dans la grille (remplace le plafond_produit global)

Revision ID: c1f8e5a3d947
Revises: 6a7e2f4c9b1d
Create Date: 2026-08-05 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "c1f8e5a3d947"
down_revision: str | None = "6a7e2f4c9b1d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Migration de donnees uniquement (seuils est deja JSONB libre, aucun ALTER TABLE necessaire).
# Valeurs de reference du catalogue CORE-SIM (simulateur/config/config.yaml) : un seed pour
# initialiser la grille existante, pas une dependance runtime a CORE-SIM.
PLAFONDS_PRODUITS_INITIAUX = {
    "prod-salarie": 2_000_000,
    "prod-individuel": 2_000_000,
    "prod-jeune": 750_000,
    "prod-femme-gie": 1_500_000,
    "prod-agricole": 1_500_000,
}


def upgrade() -> None:
    op.execute(
        text("""
            UPDATE grille_decision
            SET seuils = (seuils - 'plafond_produit')
                || jsonb_build_object('plafonds_produits', :plafonds)
        """).bindparams(bindparam("plafonds", value=PLAFONDS_PRODUITS_INITIAUX, type_=JSONB))
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE grille_decision
        SET seuils = (seuils - 'plafonds_produits') || jsonb_build_object('plafond_produit', 3000000)
        """
    )
