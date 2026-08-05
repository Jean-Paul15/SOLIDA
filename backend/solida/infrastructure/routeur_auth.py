import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from solida.adapters.persistence.journal_audit_sql import JournalAuditSql
from solida.adapters.persistence.modeles_sqlalchemy import AccessToken, Utilisateur
from solida.domain.erreurs import AccesRefuse
from solida.domain.rules.mot_de_passe import valider_mot_de_passe
from solida.infrastructure.auth import (
    GestionnaireUtilisateurs,
    charger_mots_de_passe_courants,
    current_active_user,
    obtenir_gestionnaire_utilisateurs,
    obtenir_session,
    obtenir_strategie,
    revoquer_jetons_utilisateur,
    transport_cookie,
)
from solida.infrastructure.dependances import journal_audit

routeur = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class DemandeConnexion(BaseModel):
    identifiant: str
    mot_de_passe: str


class ReponseConnexion(BaseModel):
    nom: str
    agence: str | None
    doit_changer_mot_de_passe: bool


class DemandeChangementMotDePasse(BaseModel):
    mot_de_passe_actuel: str
    nouveau_mot_de_passe: str


def _poser_cookie(reponse: Response, jeton: str) -> None:
    reponse.set_cookie(
        transport_cookie.cookie_name,
        jeton,
        max_age=transport_cookie.cookie_max_age,
        path=transport_cookie.cookie_path,
        domain=transport_cookie.cookie_domain,
        secure=transport_cookie.cookie_secure,
        httponly=transport_cookie.cookie_httponly,
        samesite=transport_cookie.cookie_samesite,
    )


LIMITE_ECHECS_CONNEXION = 5
FENETRE_VERROUILLAGE = timedelta(minutes=15)


@routeur.post("/connexion", response_model=ReponseConnexion)
async def connexion(
    demande: DemandeConnexion,
    reponse: Response,
    session: AsyncSession = Depends(obtenir_session),
    gestionnaire: GestionnaireUtilisateurs = Depends(obtenir_gestionnaire_utilisateurs),
    strategie: DatabaseStrategy[Utilisateur, uuid.UUID, AccessToken] = Depends(obtenir_strategie),
    audit: JournalAuditSql = Depends(journal_audit),
) -> ReponseConnexion:
    depuis = datetime.now(UTC) - FENETRE_VERROUILLAGE
    echecs_recents = audit.compter_evenements_recents(
        "connexion_echouee", demande.identifiant, depuis
    )
    if echecs_recents >= LIMITE_ECHECS_CONNEXION:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Compte temporairement bloqué après plusieurs échecs, réessayez plus tard.",
        )

    utilisateur = await gestionnaire.authentifier_par_identifiant(
        demande.identifiant, demande.mot_de_passe
    )
    if utilisateur is None or not utilisateur.is_active:
        audit.enregistrer_evenement(
            "connexion_echouee", demande.identifiant, demande.identifiant, {}
        )
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Identifiant ou mot de passe incorrect."
        )

    # Une seule session active par compte : la nouvelle connexion révoque les précédentes.
    await revoquer_jetons_utilisateur(session, utilisateur.id)
    jeton = await strategie.write_token(utilisateur)
    _poser_cookie(reponse, jeton)
    audit.enregistrer_evenement("connexion_reussie", str(utilisateur.id), demande.identifiant, {})
    return ReponseConnexion(
        nom=utilisateur.nom_complet,
        agence=utilisateur.agence_id,
        doit_changer_mot_de_passe=utilisateur.doit_changer_mot_de_passe,
    )


@routeur.post("/deconnexion")
async def deconnexion(
    requete: Request,
    reponse: Response,
    utilisateur: Utilisateur = Depends(current_active_user),
    strategie: DatabaseStrategy[Utilisateur, uuid.UUID, AccessToken] = Depends(obtenir_strategie),
    audit: JournalAuditSql = Depends(journal_audit),
) -> dict[str, str]:
    jeton = requete.cookies.get(transport_cookie.cookie_name)
    if jeton is not None:
        await strategie.destroy_token(jeton, utilisateur)

    reponse.delete_cookie(
        transport_cookie.cookie_name,
        path=transport_cookie.cookie_path,
        domain=transport_cookie.cookie_domain,
        secure=transport_cookie.cookie_secure,
        httponly=transport_cookie.cookie_httponly,
        samesite=transport_cookie.cookie_samesite,
    )
    audit.enregistrer_evenement("deconnexion", str(utilisateur.id), utilisateur.identifiant, {})
    return {"statut": "ok"}


@routeur.get("/moi", response_model=ReponseConnexion)
async def moi(utilisateur: Utilisateur = Depends(current_active_user)) -> ReponseConnexion:
    return ReponseConnexion(
        nom=utilisateur.nom_complet,
        agence=utilisateur.agence_id,
        doit_changer_mot_de_passe=utilisateur.doit_changer_mot_de_passe,
    )


@routeur.post("/changer-mot-de-passe")
async def changer_mot_de_passe(
    demande: DemandeChangementMotDePasse,
    session: AsyncSession = Depends(obtenir_session),
    utilisateur: Utilisateur = Depends(current_active_user),
    gestionnaire: GestionnaireUtilisateurs = Depends(obtenir_gestionnaire_utilisateurs),
    audit: JournalAuditSql = Depends(journal_audit),
) -> dict[str, str]:
    # Le mot de passe actuel est exigé même en session déjà authentifiée : défense en
    # profondeur contre une session volée/laissée ouverte (OWASP Session Management).
    reverifie = await gestionnaire.authentifier_par_identifiant(
        utilisateur.identifiant, demande.mot_de_passe_actuel
    )
    if reverifie is None:
        raise AccesRefuse("Mot de passe actuel incorrect.")

    # MotDePasseInvalide (ErreurDomaine) est traduite en JSON {code, message} par le
    # gestionnaire d'exceptions global de l'application — pas besoin de la rattraper ici.
    valider_mot_de_passe(demande.nouveau_mot_de_passe, charger_mots_de_passe_courants())

    await gestionnaire.changer_mot_de_passe(utilisateur, demande.nouveau_mot_de_passe)
    # Le changement de mot de passe coupe les sessions ouvertes ailleurs, y compris la
    # session courante — l'agent devra se reconnecter avec le nouveau mot de passe.
    await revoquer_jetons_utilisateur(session, utilisateur.id)
    audit.enregistrer_evenement(
        "mot_de_passe_change", str(utilisateur.id), utilisateur.identifiant, {}
    )
    return {"statut": "ok"}
