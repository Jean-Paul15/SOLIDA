import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from solida.adapters.persistence.audit_log_sql import SqlAuditLog
from solida.adapters.persistence.orm_models import AccessToken, User
from solida.domain.errors import AccesRefuse
from solida.domain.rules.mot_de_passe import valider_mot_de_passe
from solida.infrastructure.auth import (
    UserManager,
    cookie_transport,
    get_session,
    get_strategy,
    get_user_manager,
    load_common_passwords,
    revoke_user_tokens,
)
from solida.infrastructure.auth.dependencies import client_ip_address, current_active_user
from solida.infrastructure.dependencies import audit_log

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    identifiant: str
    mot_de_passe: str


class LoginResponse(BaseModel):
    name: str
    role: str
    agence: str | None
    must_change_password: bool


class ChangePasswordRequest(BaseModel):
    mot_de_passe_actuel: str
    nouveau_mot_de_passe: str


def _set_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        cookie_transport.cookie_name,
        token,
        max_age=cookie_transport.cookie_max_age,
        path=cookie_transport.cookie_path,
        domain=cookie_transport.cookie_domain,
        secure=cookie_transport.cookie_secure,
        httponly=cookie_transport.cookie_httponly,
        samesite=cookie_transport.cookie_samesite,
    )


LOGIN_FAILURE_LIMIT = 5
LOCKOUT_WINDOW = timedelta(minutes=15)


@router.post("/login", response_model=LoginResponse)
async def login(
    demande: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
    manager: UserManager = Depends(get_user_manager),
    strategy: DatabaseStrategy[User, uuid.UUID, AccessToken] = Depends(get_strategy),
    audit: SqlAuditLog = Depends(audit_log),
) -> LoginResponse:
    ip = client_ip_address(request)
    # Navigateur declare (User-Agent), pas une empreinte technique (canvas/WebGL/polices) :
    # juste l'en-tete standard, deja envoye par tout client HTTP a chaque requete. Suffisant
    # pour signaler "connexion depuis un appareil inhabituel" sans collecte intrusive.
    user_agent = request.headers.get("user-agent")
    # Le verrou porte sur identifiant+IP, pas identifiant seul : sinon n'importe qui connaissant
    # un identifiant peut le verrouiller 15 min sans avoir de compte, depuis n'importe quelle IP.
    # Contrepartie assumee : un attaquant reparti sur plusieurs IP a son propre compteur par IP
    # (protection contre le brute-force distribue legerement affaiblie), cf.
    # docs/backend/03-decisions-provisoires-a-revoir.md.
    lockout_key = f"{demande.identifiant}:{ip}"
    since = datetime.now(UTC) - LOCKOUT_WINDOW
    recent_failures = audit.compter_evenements_recents("connexion_echouee", lockout_key, since)
    if recent_failures >= LOGIN_FAILURE_LIMIT:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Compte temporairement bloqué après plusieurs échecs, réessayez plus tard.",
        )

    user = await manager.authenticate_by_identifier(demande.identifiant, demande.mot_de_passe)
    if user is None or not user.is_active:
        audit.enregistrer_evenement(
            "connexion_echouee",
            demande.identifiant,
            lockout_key,
            {"navigateur": user_agent},
            ip,
        )
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiant ou mot de passe incorrect.")

    # Une seule session active par compte : la nouvelle connexion révoque les précédentes.
    await revoke_user_tokens(session, user.id)
    token = await strategy.write_token(user)
    _set_cookie(response, token)
    audit.enregistrer_evenement(
        "connexion_reussie",
        str(user.id),
        demande.identifiant,
        {"navigateur": user_agent},
        ip,
    )
    return LoginResponse(
        name=user.nom_complet,
        role=user.role,
        agence=user.agence_id,
        must_change_password=user.doit_changer_mot_de_passe,
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user: User = Depends(current_active_user),
    strategy: DatabaseStrategy[User, uuid.UUID, AccessToken] = Depends(get_strategy),
    audit: SqlAuditLog = Depends(audit_log),
) -> dict[str, str]:
    token = request.cookies.get(cookie_transport.cookie_name)
    if token is not None:
        await strategy.destroy_token(token, user)

    response.delete_cookie(
        cookie_transport.cookie_name,
        path=cookie_transport.cookie_path,
        domain=cookie_transport.cookie_domain,
        secure=cookie_transport.cookie_secure,
        httponly=cookie_transport.cookie_httponly,
        samesite=cookie_transport.cookie_samesite,
    )
    audit.enregistrer_evenement(
        "deconnexion",
        str(user.id),
        user.identifiant,
        {"navigateur": request.headers.get("user-agent")},
        client_ip_address(request),
    )
    return {"statut": "ok"}


@router.get("/me", response_model=LoginResponse)
async def me(user: User = Depends(current_active_user)) -> LoginResponse:
    return LoginResponse(
        name=user.nom_complet,
        role=user.role,
        agence=user.agence_id,
        must_change_password=user.doit_changer_mot_de_passe,
    )


@router.post("/change-password")
async def change_password(
    demande: ChangePasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(current_active_user),
    manager: UserManager = Depends(get_user_manager),
    audit: SqlAuditLog = Depends(audit_log),
) -> dict[str, str]:
    # Le mot de passe actuel est exigé même en session déjà authentifiée : défense en
    # profondeur contre une session volée/laissée ouverte (OWASP Session Management).
    reauthenticated = await manager.authenticate_by_identifier(
        user.identifiant, demande.mot_de_passe_actuel
    )
    if reauthenticated is None:
        raise AccesRefuse("Mot de passe actuel incorrect.")

    # MotDePasseInvalide (DomainError) est traduite en JSON {code, message} par le
    # gestionnaire d'exceptions global de l'application — pas besoin de la rattraper ici.
    valider_mot_de_passe(demande.nouveau_mot_de_passe, load_common_passwords())

    await manager.change_password(user, demande.nouveau_mot_de_passe)
    # Le changement de mot de passe coupe les sessions ouvertes ailleurs, y compris la
    # session courante — l'agent devra se reconnecter avec le nouveau mot de passe.
    await revoke_user_tokens(session, user.id)
    audit.enregistrer_evenement(
        "mot_de_passe_change",
        str(user.id),
        user.identifiant,
        {"navigateur": request.headers.get("user-agent")},
        client_ip_address(request),
    )
    return {"statut": "ok"}
