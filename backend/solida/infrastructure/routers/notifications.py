from fastapi import APIRouter, Depends, HTTPException, Query, status

from solida.adapters.http import mappers
from solida.adapters.http.schemas.notifications import PageNotifications
from solida.adapters.persistence.orm_models import User
from solida.application.use_cases.archiver_notification import ArchiverNotification
from solida.application.use_cases.assigner_notification import AssignerNotification
from solida.application.use_cases.lister_notifications import ListerNotifications
from solida.infrastructure.auth.dependencies import require_role
from solida.infrastructure.dependencies import (
    archiver_notification,
    assigner_notification,
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
    user: User = Depends(require_role("agent")),
    use_case: ListerNotifications = Depends(lister_notifications),
) -> PageNotifications:
    demandes, total = use_case.execute(user.agence_id, limite, decalage)
    return PageNotifications(
        elements=[mappers.demande_to_notification(d) for d in demandes], total=total
    )


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
    user: User = Depends(require_role("agent")),
    use_case: AssignerNotification = Depends(assigner_notification),
) -> dict[str, str | None]:
    demande = use_case.execute(demande_id, str(user.id), user.agence_id)
    if demande is None:
        raise _not_found_error()
    return {"assigne_a_agent_id": demande.assigne_a_agent_id}
