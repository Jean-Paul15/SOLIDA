"""grille a trois tranches (accord / accord_sous_condition / refus)

Revision ID: b7c3d8e1f420
Revises: e5a1c9f04b3d
Create Date: 2026-09-14 15:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "b7c3d8e1f420"
down_revision: str | None = "e5a1c9f04b3d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Migration de donnees uniquement (seuils est deja JSONB libre, aucun ALTER TABLE necessaire).
#
# La tranche COMITE_DE_CREDIT est supprimee : le comite de credit valide deja chaque tranche
# (03-MODELE/11-formule-cible-credit-progressif.md), ce n'etait donc pas une zone de decision
# distincte. L'ancienne zone d'examen (multiplicateur_examen = 1.6) est fusionnee dans REFUS,
# dont la frontiere devient le seuil economique pur (multiplicateur implicite de 1,
# equivalent a l'ancien multiplicateur_vigilance qui n'etait de toute facon pas editable).
# `multiplicateur_vigilance` et `multiplicateur_examen` n'ont donc plus de sens dans les
# seuils stockes : retires plutot que laisses en champs morts.


def upgrade() -> None:
    op.execute(
        """
        UPDATE grille_decision
        SET seuils = (seuils - 'multiplicateur_vigilance') - 'multiplicateur_examen'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE grille_decision
        SET seuils = seuils
            || jsonb_build_object('multiplicateur_vigilance', 1.0)
            || jsonb_build_object('multiplicateur_examen', 1.6)
        """
    )
