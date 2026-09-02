"""Opérations SQL réservées à l'administration manuelle des comptes."""

import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import sqlalchemy as sa
from fastapi_users.password import PasswordHelper

from solida.adapters.persistence.orm_models import ROLES_VALIDES
from solida.infrastructure.database import solida_engine
from solida.infrastructure.fixtures.comptes_demo import COMPTES_DEMO, MOT_DE_PASSE_DEMO


@dataclass(frozen=True)
class LockedAccount:
    identifiant: str
    nom_complet: str
    role: str
    agence_id: str | None
    desactive_le: datetime | None


def _generate_password() -> str:
    return secrets.token_urlsafe(12)


def create_account(
    identifiant: str,
    nom_complet: str,
    role: str,
    agence_id: str | None,
    email: str | None = None,
    mot_de_passe: str | None = None,
    doit_changer_mot_de_passe: bool = True,
) -> str:
    """Crée ou actualise un compte et renvoie son mot de passe initial uniquement."""
    if role not in ROLES_VALIDES:
        raise SystemExit(f"Rôle invalide : {role!r}. Attendu : {ROLES_VALIDES}.")

    password = mot_de_passe or _generate_password()
    password_hash = PasswordHelper().hash(password)
    statement = sa.text("""
        INSERT INTO utilisateur
            (id, identifiant, nom_complet, role, agence_id, email,
             hashed_password, is_active, is_superuser, is_verified,
             doit_changer_mot_de_passe)
        VALUES
            (:id, :identifiant, :nom_complet, :role, :agence_id, :email,
             :hashed_password, true, false, true, :doit_changer_mot_de_passe)
        ON CONFLICT (identifiant) DO UPDATE SET
            nom_complet = excluded.nom_complet,
            role = excluded.role,
            agence_id = excluded.agence_id,
            doit_changer_mot_de_passe = excluded.doit_changer_mot_de_passe
    """)
    with solida_engine().begin() as connection:
        connection.execute(
            statement,
            {
                "id": uuid.uuid4(),
                "identifiant": identifiant,
                "nom_complet": nom_complet,
                "role": role,
                "agence_id": agence_id,
                "email": email or f"{identifiant}@solida.local",
                "hashed_password": password_hash,
                "doit_changer_mot_de_passe": doit_changer_mot_de_passe,
            },
        )
    return password


def provision_demo() -> None:
    for account in COMPTES_DEMO:
        create_account(
            identifiant=account["identifiant"] or "",
            nom_complet=account["nom_complet"] or "",
            role=account["role"] or "",
            agence_id=account["agence_id"],
            email=account["email"],
            mot_de_passe=MOT_DE_PASSE_DEMO,
            doit_changer_mot_de_passe=False,
        )


def lock_account(identifiant: str) -> None:
    with solida_engine().begin() as connection:
        row = connection.execute(
            sa.text("""
                UPDATE utilisateur SET is_active = false, desactive_le = :maintenant
                WHERE identifiant = :identifiant
                RETURNING id
            """),
            {"maintenant": datetime.now(UTC), "identifiant": identifiant},
        ).first()
        if row is None:
            raise SystemExit(f"Aucun compte avec l'identifiant '{identifiant}'.")
        connection.execute(sa.text("DELETE FROM access_token WHERE user_id = :id"), {"id": row.id})


def list_locked_accounts() -> list[LockedAccount]:
    """Renvoie les comptes désactivés sans effectuer de modification."""
    with solida_engine().connect() as connection:
        rows = connection.execute(
            sa.text("""
                SELECT identifiant, nom_complet, role, agence_id, desactive_le
                FROM utilisateur
                WHERE is_active = false
                ORDER BY desactive_le DESC NULLS LAST
            """)
        )
        return [
            LockedAccount(
                identifiant=row.identifiant,
                nom_complet=row.nom_complet,
                role=row.role,
                agence_id=row.agence_id,
                desactive_le=row.desactive_le,
            )
            for row in rows
        ]


def unlock_account(identifiant: str) -> None:
    with solida_engine().begin() as connection:
        row = connection.execute(
            sa.text("""
                UPDATE utilisateur SET is_active = true, desactive_le = NULL
                WHERE identifiant = :identifiant
                RETURNING id
            """),
            {"identifiant": identifiant},
        ).first()
        if row is None:
            raise SystemExit(f"Aucun compte avec l'identifiant '{identifiant}'.")
