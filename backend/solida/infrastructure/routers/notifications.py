from fastapi import APIRouter, Depends, HTTPException, Query, status

from solida.adapters.http import mappers
from solida.adapters.http.schemas.notifications import (
    AgentAgence,
    AssignerNotificationRequest,
    PageNotifications,
)
from solida.adapters.persistence.orm_models import User
from solida.application.use_cases.archiver_notification import ArchiverNotification
from solida.application.use_cases.assigner_notification import AssignerNotification
from solida.application.use_cases.lister_agents_agence import ListerAgentsAgence
from solida.application.use_cases.lister_notifications import ListerNotifications
from solida.infrastructure.auth.dependencies import require_role
from solida.infrastructure.dependencies import (
    archiver_notification,
    assigner_notification,
    lister_agents_agence,
    lister_notifications,
)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


def _not_found_error() -> HTTPException:
    return HTTPException(
        status.HTTP_404_NOT_FOUND,
        detail={"code": "introuvable", "message": "Aucune notification ne correspond."},
    )


@router.get("", response_model=PageNotifications)
def lister(
    limite: int = Query(default=20, ge=0, le=50),
    decalage: int = Query(default=0, ge=0),
    user: User = Depends(require_role("agent", "superviseur")),
    use_case: ListerNotifications = Depends(lister_notifications),
) -> PageNotifications:
    demandes, total = use_case.execute(user.role, str(user.id), user.agence_id, limite, decalage)
    return PageNotifications(
        elements=[mappers.demande_to_notification(d) for d in demandes], total=total
    )


@router.get("/agents", response_model=list[AgentAgence])
def lister_agents(
    agence_id: str | None = Query(default=None),
    user: User = Depends(require_role("superviseur")),
    use_case: ListerAgentsAgence = Depends(lister_agents_agence),
) -> list[AgentAgence]:
    """Un superviseur d'agence n'a jamais le choix : sa propre agence, quoi que dise le
    paramètre. Un superviseur réseau (`agence_id is None`) doit préciser l'agence via le
    paramètre — il voit des demandes de plusieurs agences dans sa liste."""
    if user.agence_id is not None:
        cible = user.agence_id
    elif agence_id is not None:
        cible = agence_id
    else:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "agence_requise",
                "message": "Un superviseur réseau doit préciser une agence pour lister ses agents.",
            },
        )
    agents = use_case.execute(cible)
    return [AgentAgence(id=a.id, nom_complet=a.nom_complet) for a in agents]


@router.post("/{demande_id}/archiver")
def archiver(
    demande_id: str,
    user: User = Depends(require_role("agent")),
    use_case: ArchiverNotification = Depends(archiver_notification),
) -> dict[str, str]:
    demande = use_case.execute(demande_id, str(user.id), user.agence_id)
    if demande is None:
        raise _not_found_error()
    return {"statut": demande.statut}


@router.post("/{demande_id}/assigner")
def assigner(
    demande_id: str,
    corps: AssignerNotificationRequest,
    user: User = Depends(require_role("superviseur")),
    use_case: AssignerNotification = Depends(assigner_notification),
) -> dict[str, str | None]:
    demande = use_case.execute(demande_id, user.agence_id, corps.agent_id)
    if demande is None:
        raise _not_found_error()
    return {"assigne_a_agent_id": demande.assigne_a_agent_id}
