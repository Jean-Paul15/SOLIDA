"""objets implicites par produit dans la grille

Revision ID: c4e9a2f7b118
Revises: b7c3d8e1f420
Create Date: 2026-09-14 19:30:00.000000

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "c4e9a2f7b118"
down_revision: str | None = "b7c3d8e1f420"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Migration de donnees uniquement (seuils est deja JSONB libre, aucun ALTER TABLE necessaire).
#
# objets_implicites_produits : produit_id -> objet_credit, pour les produits dont le nom
# determine deja l'objet du credit (ex. un futur "Credit agricole" impliquant
# "intrants_agricoles"). Meme statut que "classification_objets" (voir e5a1c9f04b3d) : demarre
# vide, aucune correspondance n'est devinee depuis le libelle du produit tant que la
# cooperative ne l'a pas confirmee produit par produit.


def upgrade() -> None:
    op.execute(
        text("""
            UPDATE grille_decision
            SET seuils = seuils || jsonb_build_object('objets_implicites_produits', :vide)
        """).bindparams(bindparam("vide", value={}, type_=JSONB))
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE grille_decision
        SET seuils = seuils - 'objets_implicites_produits'
        """
    )
