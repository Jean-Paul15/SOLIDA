import re
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from solida.adapters.http import mappers
from solida.adapters.http.auth_dependencies import client_ip_address, current_active_user
from solida.adapters.http.schemas.societaires import DossierSocietaire, SocietaireSearchResult
from solida.adapters.persistence.audit_log_sql import SqlAuditLog
from solida.adapters.persistence.orm_models import User
from solida.application.use_cases.consulter_dossier import ConsulterDossier
from solida.application.use_cases.lister_societaires_recents import ListerSocietairesRecents
from solida.application.use_cases.rechercher_societaire import RechercherSocietaire
from solida.domain.errors import AccesRefuse
from solida.infrastructure.dependencies import (
    audit_log,
    consulter_dossier,
    lister_societaires_recents,
    rechercher_societaire,
)

router = APIRouter(prefix="/api/v1/societaires", tags=["societaires"])


def _agence_agent(user: User) -> str | None:
    """`None` pour tout rôle qui n'est pas cloisonné par agence : `agent` seulement."""
    return user.agence_id if user.role == "agent" else None


_FORME_IDENTIFIANT = re.compile(r"^[A-Za-z0-9_-]{1,50}$")


def _valider_forme_identifiant(societaire_id: str) -> None:
    """Rejette explicitement un identifiant de forme inattendue (ex. un `/` encodé) avant
    toute requête DB : sans ça, un caractère hors de ce format remonte en 500 générique au
    lieu d'un 422 propre plus bas dans la pile."""
    if not _FORME_IDENTIFIANT.match(societaire_id):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "identifiant_invalide",
                "message": "L'identifiant du sociétaire n'est pas d'une forme valide.",
            },
        )


@router.get("/search")
def search(
    requete: Request,
    terme: str = "",
    # Plafond serveur : un compte superviseur/auditeur/administrateur n'est pas cloisonne par
    # agence, `limite` doit donc etre borne independamment de ce que le client demande. ge=0 :
    # une valeur negative atteignait le LIMIT SQL et remontait en 500 brut.
    limite: int = Query(default=10, ge=0, le=50),
    user: User = Depends(current_active_user),
    cas_usage: RechercherSocietaire = Depends(rechercher_societaire),
    audit: SqlAuditLog = Depends(audit_log),
) -> dict[str, object]:
    agence_agent = _agence_agent(user)
    resultats = cas_usage.execute(terme, limite, agence_agent)
    audit.enregistrer_evenement(
        "recherche_societaires",
        str(user.id),
        terme,
        {
            "nombre_resultats": len(resultats),
            # Contexte pour une revue humaine d'une alerte de volume, pas un filtre : un
            # User-Agent se falsifie en une ligne (curl -H "User-Agent: ..."), jamais un
            # critere de blocage automatique a lui seul.
            "navigateur": requete.headers.get("user-agent"),
        },
        client_ip_address(requete),
    )
    return {
        "elements": [SocietaireSearchResult.model_validate(asdict(r)) for r in resultats],
        "total": cas_usage.compter(terme, agence_agent),
    }


@router.get("/recent")
def recent(
    user: User = Depends(current_active_user),
    cas_usage: ListerSocietairesRecents = Depends(lister_societaires_recents),
) -> dict[str, object]:
    resultats = cas_usage.execute(str(user.id))
    return {"elements": [SocietaireSearchResult.model_validate(asdict(r)) for r in resultats]}


@router.get("/{societaire_id}/dossier", response_model=DossierSocietaire)
def dossier(
    societaire_id: str,
    requete: Request,
    user: User = Depends(current_active_user),
    cas_usage: ConsulterDossier = Depends(consulter_dossier),
    audit: SqlAuditLog = Depends(audit_log),
) -> DossierSocietaire:
    _valider_forme_identifiant(societaire_id)
    resultat = cas_usage.execute(societaire_id)
    if resultat is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail={
                "code": "introuvable",
                "message": "Aucun sociétaire ne correspond à cet identifiant.",
            },
        )

    agence_agent = _agence_agent(user)
    if agence_agent is not None and resultat.identite.agence != agence_agent:
        raise AccesRefuse("Ce sociétaire n'appartient pas à votre agence.")

    audit.enregistrer_evenement(
        "consultation_dossier",
        str(user.id),
        societaire_id,
        {"navigateur": requete.headers.get("user-agent")},
        client_ip_address(requete),
    )
    return mappers.dossier_to_schema(resultat)


@router.get("/{societaire_id}/groupe")
def groupe(
    societaire_id: str,
    user: User = Depends(current_active_user),
    cas_usage: ConsulterDossier = Depends(consulter_dossier),
) -> dict[str, object]:
    _valider_forme_identifiant(societaire_id)
    resultat = cas_usage.execute(societaire_id)
    if resultat is None or resultat.identite.segment != "femme_gie" or resultat.groupe is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail={
                "code": "sans_groupe",
                "message": "Ce sociétaire n'appartient à aucun groupe actif.",
            },
        )

    agence_agent = _agence_agent(user)
    if agence_agent is not None and resultat.identite.agence != agence_agent:
        raise AccesRefuse("Ce sociétaire n'appartient pas à votre agence.")

    return mappers.groupe_to_schema(resultat.groupe).model_dump()
