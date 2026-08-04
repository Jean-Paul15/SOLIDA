import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from pydantic import BaseModel

from solida.adapters.persistence.modeles_sqlalchemy import AccessToken, Utilisateur
from solida.infrastructure.auth import (
    GestionnaireUtilisateurs,
    current_active_user,
    obtenir_gestionnaire_utilisateurs,
    obtenir_strategie,
    transport_cookie,
)

routeur = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class DemandeConnexion(BaseModel):
    identifiant: str
    mot_de_passe: str


class ReponseConnexion(BaseModel):
    nom: str
    agence: str | None


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


@routeur.post("/connexion", response_model=ReponseConnexion)
async def connexion(
    demande: DemandeConnexion,
    reponse: Response,
    gestionnaire: GestionnaireUtilisateurs = Depends(obtenir_gestionnaire_utilisateurs),
    strategie: DatabaseStrategy[Utilisateur, uuid.UUID, AccessToken] = Depends(obtenir_strategie),
) -> ReponseConnexion:
    utilisateur = await gestionnaire.authentifier_par_identifiant(
        demande.identifiant, demande.mot_de_passe
    )
    if utilisateur is None or not utilisateur.is_active:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Identifiant ou mot de passe incorrect."
        )

    jeton = await strategie.write_token(utilisateur)
    _poser_cookie(reponse, jeton)
    return ReponseConnexion(nom=utilisateur.nom_complet, agence=utilisateur.agence_id)


@routeur.post("/deconnexion")
async def deconnexion(
    requete: Request,
    reponse: Response,
    utilisateur: Utilisateur = Depends(current_active_user),
    strategie: DatabaseStrategy[Utilisateur, uuid.UUID, AccessToken] = Depends(obtenir_strategie),
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
    return {"statut": "ok"}


@routeur.get("/moi", response_model=ReponseConnexion)
async def moi(utilisateur: Utilisateur = Depends(current_active_user)) -> ReponseConnexion:
    return ReponseConnexion(nom=utilisateur.nom_complet, agence=utilisateur.agence_id)
