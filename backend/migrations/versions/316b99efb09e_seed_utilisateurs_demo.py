"""seed utilisateurs demo

Revision ID: 316b99efb09e
Revises: a2ec84e2d9d6
Create Date: 2026-08-04 21:10:00.000000

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from fastapi_users.password import PasswordHelper

revision: str = "316b99efb09e"
down_revision: str | None = "a2ec84e2d9d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Un compte de demonstration par role, mot de passe identique pour tous : "solida-demo".
# Reprend les deux agents deja utilises par le mock frontend (identifiant, nom inchanges),
# mais agence_id doit etre un vrai code caisse_id de CORE-SIM (CAI-00 a CAI-07) : c'est sur
# cette valeur que le cloisonnement par agence de l'agent est verifie a chaque requete.
_UTILISATEURS_DEMO = [
    {
        "identifiant": "agent.be",
        "email": "agent.be@solida.local",
        "nom_complet": "Agent Bè",
        "role": "agent",
        "agence_id": "CAI-00",
    },
    {
        "identifiant": "agent.agoe",
        "email": "agent.agoe@solida.local",
        "nom_complet": "Agent Agoè",
        "role": "agent",
        "agence_id": "CAI-01",
    },
    {
        "identifiant": "superviseur.reseau",
        "email": "superviseur.reseau@solida.local",
        "nom_complet": "Superviseur Réseau",
        "role": "superviseur",
        "agence_id": None,
    },
    {
        "identifiant": "auditeur.interne",
        "email": "auditeur.interne@solida.local",
        "nom_complet": "Auditeur Interne",
        "role": "auditeur",
        "agence_id": None,
    },
    {
        "identifiant": "administrateur.systeme",
        "email": "administrateur.systeme@solida.local",
        "nom_complet": "Administrateur Système",
        "role": "administrateur",
        "agence_id": None,
    },
]

_MOT_DE_PASSE_DEMO = "solida-demo"


def upgrade() -> None:
    hacheur = PasswordHelper()
    connexion = op.get_bind()
    for utilisateur in _UTILISATEURS_DEMO:
        connexion.execute(
            sa.text(
                """
                INSERT INTO utilisateur
                    (id, identifiant, nom_complet, role, agence_id, email,
                     hashed_password, is_active, is_superuser, is_verified)
                VALUES
                    (:id, :identifiant, :nom_complet, :role, :agence_id, :email,
                     :hashed_password, true, false, true)
                """
            ),
            {
                "id": uuid.uuid4(),
                "identifiant": utilisateur["identifiant"],
                "nom_complet": utilisateur["nom_complet"],
                "role": utilisateur["role"],
                "agence_id": utilisateur["agence_id"],
                "email": utilisateur["email"],
                "hashed_password": hacheur.hash(_MOT_DE_PASSE_DEMO),
            },
        )


def downgrade() -> None:
    connexion = op.get_bind()
    connexion.execute(
        sa.text("DELETE FROM utilisateur WHERE identifiant = ANY(:identifiants)"),
        {"identifiants": [u["identifiant"] for u in _UTILISATEURS_DEMO]},
    )
