import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from solida.adapters.persistence.audit_log_sql import SqlAuditLog
from solida.adapters.persistence.modeles_sqlalchemy import AccessToken, Utilisateur
from solida.domain.erreurs import AccesRefuse
from solida.domain.rules.mot_de_passe import valider_mot_de_passe
from solida.infrastructure.auth import (
    UserManager,
    client_ip_address,
    cookie_transport,
    current_active_user,
    get_session,
    get_strategy,
    get_user_manager,
    load_common_passwords,
    revoke_user_tokens,
)
from solida.infrastructure.dependances import audit_log

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class DemandeConnexion(BaseModel):
    identifiant: str
    mot_de_passe: str


class ReponseConnexion(BaseModel):
    nom: str
    role: str
    agence: str | None
    doit_changer_mot_de_passe: bool


class DemandeChangementMotDePasse(BaseModel):
    mot_de_passe_actuel: str
    nouveau_mot_de_passe: str


def _poser_cookie(reponse: Response, jeton: str) -> None:
    reponse.set_cookie(
        cookie_transport.cookie_name,
        jeton,
        max_age=cookie_transport.cookie_max_age,
        path=cookie_transport.cookie_path,
        domain=cookie_transport.cookie_domain,
        secure=cookie_transport.cookie_secure,
        httponly=cookie_transport.cookie_httponly,
        samesite=cookie_transport.cookie_samesite,
    )


LIMITE_ECHECS_CONNEXION = 5
FENETRE_VERROUILLAGE = timedelta(minutes=15)


@router.post("/connexion", response_model=ReponseConnexion)
async def connexion(
    demande: DemandeConnexion,
    requete: Request,
    reponse: Response,
    session: AsyncSession = Depends(get_session),
    gestionnaire: UserManager = Depends(get_user_manager),
    strategie: DatabaseStrategy[Utilisateur, uuid.UUID, AccessToken] = Depends(get_strategy),
    audit: SqlAuditLog = Depends(audit_log),
) -> ReponseConnexion:
    ip = client_ip_address(requete)
    # Navigateur declare (User-Agent), pas une empreinte technique (canvas/WebGL/polices) :
    # juste l'en-tete standard, deja envoye par tout client HTTP a chaque requete. Suffisant
    # pour signaler "connexion depuis un appareil inhabituel" sans collecte intrusive.
    navigateur = requete.headers.get("user-agent")
    # Le verrou porte sur identifiant+IP, pas identifiant seul : sinon n'importe qui connaissant
    # un identifiant peut le verrouiller 15 min sans avoir de compte, depuis n'importe quelle IP.
    # Contrepartie assumee : un attaquant reparti sur plusieurs IP a son propre compteur par IP
    # (protection contre le brute-force distribue legerement affaiblie), cf.
    # docs/backend/03-decisions-provisoires-a-revoir.md.
    cle_verrou = f"{demande.identifiant}:{ip}"
    depuis = datetime.now(UTC) - FENETRE_VERROUILLAGE
    echecs_recents = audit.compter_evenements_recents("connexion_echouee", cle_verrou, depuis)
    if echecs_recents >= LIMITE_ECHECS_CONNEXION:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Compte temporairement bloqué après plusieurs échecs, réessayez plus tard.",
        )

    utilisateur = await gestionnaire.authenticate_by_identifier(
        demande.identifiant, demande.mot_de_passe
    )
    if utilisateur is None or not utilisateur.is_active:
        audit.enregistrer_evenement(
            "connexion_echouee",
            demande.identifiant,
            cle_verrou,
            {"navigateur": navigateur},
            ip,
        )
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiant ou mot de passe incorrect.")

    # Une seule session active par compte : la nouvelle connexion révoque les précédentes.
    await revoke_user_tokens(session, utilisateur.id)
    jeton = await strategie.write_token(utilisateur)
    _poser_cookie(reponse, jeton)
    audit.enregistrer_evenement(
        "connexion_reussie",
        str(utilisateur.id),
        demande.identifiant,
        {"navigateur": navigateur},
        ip,
    )
    return ReponseConnexion(
        nom=utilisateur.nom_complet,
        role=utilisateur.role,
        agence=utilisateur.agence_id,
        doit_changer_mot_de_passe=utilisateur.doit_changer_mot_de_passe,
    )


@router.post("/deconnexion")
async def deconnexion(
    requete: Request,
    reponse: Response,
    utilisateur: Utilisateur = Depends(current_active_user),
    strategie: DatabaseStrategy[Utilisateur, uuid.UUID, AccessToken] = Depends(get_strategy),
    audit: SqlAuditLog = Depends(audit_log),
) -> dict[str, str]:
    jeton = requete.cookies.get(cookie_transport.cookie_name)
    if jeton is not None:
        await strategie.destroy_token(jeton, utilisateur)

    reponse.delete_cookie(
        cookie_transport.cookie_name,
        path=cookie_transport.cookie_path,
        domain=cookie_transport.cookie_domain,
        secure=cookie_transport.cookie_secure,
        httponly=cookie_transport.cookie_httponly,
        samesite=cookie_transport.cookie_samesite,
    )
    audit.enregistrer_evenement(
        "deconnexion",
        str(utilisateur.id),
        utilisateur.identifiant,
        {"navigateur": requete.headers.get("user-agent")},
        client_ip_address(requete),
    )
    return {"statut": "ok"}


@router.get("/moi", response_model=ReponseConnexion)
async def moi(utilisateur: Utilisateur = Depends(current_active_user)) -> ReponseConnexion:
    return ReponseConnexion(
        nom=utilisateur.nom_complet,
        role=utilisateur.role,
        agence=utilisateur.agence_id,
        doit_changer_mot_de_passe=utilisateur.doit_changer_mot_de_passe,
    )


@router.post("/changer-mot-de-passe")
async def changer_mot_de_passe(
    demande: DemandeChangementMotDePasse,
    requete: Request,
    session: AsyncSession = Depends(get_session),
    utilisateur: Utilisateur = Depends(current_active_user),
    gestionnaire: UserManager = Depends(get_user_manager),
    audit: SqlAuditLog = Depends(audit_log),
) -> dict[str, str]:
    # Le mot de passe actuel est exigé même en session déjà authentifiée : défense en
    # profondeur contre une session volée/laissée ouverte (OWASP Session Management).
    reverifie = await gestionnaire.authenticate_by_identifier(
        utilisateur.identifiant, demande.mot_de_passe_actuel
    )
    if reverifie is None:
        raise AccesRefuse("Mot de passe actuel incorrect.")

    # MotDePasseInvalide (ErreurDomaine) est traduite en JSON {code, message} par le
    # gestionnaire d'exceptions global de l'application — pas besoin de la rattraper ici.
    valider_mot_de_passe(demande.nouveau_mot_de_passe, load_common_passwords())

    await gestionnaire.change_password(utilisateur, demande.nouveau_mot_de_passe)
    # Le changement de mot de passe coupe les sessions ouvertes ailleurs, y compris la
    # session courante — l'agent devra se reconnecter avec le nouveau mot de passe.
    await revoke_user_tokens(session, utilisateur.id)
    audit.enregistrer_evenement(
        "mot_de_passe_change",
        str(utilisateur.id),
        utilisateur.identifiant,
        {"navigateur": requete.headers.get("user-agent")},
        client_ip_address(requete),
    )
    return {"statut": "ok"}
