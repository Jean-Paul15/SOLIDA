"""politique de mot de passe et de session

Revision ID: 9d4a1f2b7c3e
Revises: f7e6a07b7371
Create Date: 2026-08-05 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "9d4a1f2b7c3e"
down_revision: str | None = "f7e6a07b7371"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # server_default=true backfille aussi les comptes deja seedes par 316b99efb09e :
    # ils doivent changer leur mot de passe partage au meme titre que tout nouveau compte.
    op.add_column(
        "utilisateur",
        sa.Column(
            "doit_changer_mot_de_passe", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
    )
    op.add_column(
        "utilisateur",
        sa.Column("mot_de_passe_modifie_le", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "utilisateur",
        sa.Column("desactive_le", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "access_token",
        sa.Column(
            "derniere_activite_le",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    # user_id n'avait pas d'index malgre la FK : necessaire pour revoquer les jetons
    # d'un utilisateur (nouvelle connexion, changement de mot de passe) sans scanner la table.
    op.create_index("ix_access_token_user_id", "access_token", ["user_id"])
    # Verrouillage apres echecs de connexion (type + objet=identifiant + fenetre temporelle)
    # et "societaires recents" (type + acteur_id + fenetre temporelle) : deux lectures
    # frequentes sur journal_audit, qui ne pouvait s'appuyer que sur l'index de "type" seul.
    op.create_index(
        "ix_journal_audit_type_objet_horodatage",
        "journal_audit",
        ["type", "objet", "horodatage"],
    )
    op.create_index(
        "ix_journal_audit_type_acteur_horodatage",
        "journal_audit",
        ["type", "acteur_id", "horodatage"],
    )


def downgrade() -> None:
    op.drop_index("ix_journal_audit_type_acteur_horodatage", table_name="journal_audit")
    op.drop_index("ix_journal_audit_type_objet_horodatage", table_name="journal_audit")
    op.drop_index("ix_access_token_user_id", table_name="access_token")
    op.drop_column("access_token", "derniere_activite_le")
    op.drop_column("utilisateur", "desactive_le")
    op.drop_column("utilisateur", "mot_de_passe_modifie_le")
    op.drop_column("utilisateur", "doit_changer_mot_de_passe")
