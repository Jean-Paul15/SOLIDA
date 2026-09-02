import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import cast

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin, exceptions
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from solida.adapters.persistence.orm_models import AccessToken, User
from solida.infrastructure.auth.session import get_user_db
from solida.infrastructure.config import Configuration

_COMMON_PASSWORDS_FILE = Path(__file__).parent.parent / "mots_de_passe_courants.txt"
_configuration = Configuration()


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = _configuration.secret_auth
    verification_token_secret = _configuration.secret_auth

    async def _get_by_identifier(self, identifiant: str) -> User | None:
        # fastapi-users expose une abstraction ; cette application injecte SQLAlchemy.
        user_db = cast(SQLAlchemyUserDatabase[User, uuid.UUID], self.user_db)
        statement = select(User).where(User.identifiant == identifiant)
        result = await user_db.session.execute(statement)
        return result.scalar_one_or_none()

    async def authenticate_by_identifier(self, identifiant: str, mot_de_passe: str) -> User | None:
        """Authentifie par identifiant sans révéler son existence par le temps de réponse."""
        user = await self._get_by_identifier(identifiant)
        if user is None:
            self.password_helper.hash(mot_de_passe)
            return None

        verified, updated_hash = self.password_helper.verify_and_update(
            mot_de_passe, user.hashed_password
        )
        if not verified:
            return None
        if updated_hash is not None:
            await self.user_db.update(user, {"hashed_password": updated_hash})
        return user

    async def get_by_identifier(self, identifiant: str) -> User:
        user = await self._get_by_identifier(identifiant)
        if user is None:
            raise exceptions.UserNotExists()
        return user

    async def change_password(self, user: User, nouveau_mot_de_passe: str) -> None:
        password_hash = self.password_helper.hash(nouveau_mot_de_passe)
        await self.user_db.update(
            user,
            {
                "hashed_password": password_hash,
                "doit_changer_mot_de_passe": False,
                "mot_de_passe_modifie_le": datetime.now(UTC),
            },
        )


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


@lru_cache(maxsize=1)
def load_common_passwords() -> frozenset[str]:
    lines = _COMMON_PASSWORDS_FILE.read_text(encoding="utf-8").splitlines()
    return frozenset(line.strip().lower() for line in lines if line.strip())


async def revoke_user_tokens(session: AsyncSession, utilisateur_id: uuid.UUID) -> None:
    """Garantit une session unique après connexion ou changement de mot de passe."""
    await session.execute(delete(AccessToken).where(AccessToken.user_id == utilisateur_id))
    await session.commit()
