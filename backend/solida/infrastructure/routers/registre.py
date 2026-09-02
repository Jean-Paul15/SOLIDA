from fastapi import APIRouter, Depends, Query

from solida.adapters.http import mappers
from solida.adapters.http.schemas.registre import PageRegistre
from solida.adapters.persistence.orm_models import User
from solida.application.use_cases.lister_decisions import ListerDecisions
from solida.infrastructure.auth.dependencies import current_active_user
from solida.infrastructure.dependencies import lister_decisions

router = APIRouter(prefix="/api/v1/registre", tags=["registre"])


@router.get("", response_model=PageRegistre)
def lister(
    # Plafond serveur, meme raisonnement que societaires.py:recherche. ge=0 sur les deux :
    # une valeur negative atteignait le LIMIT/OFFSET SQL et remontait en 500 brut.
    limite: int = Query(default=20, ge=0, le=50),
    decalage: int = Query(default=0, ge=0),
    user: User = Depends(current_active_user),
    use_case: ListerDecisions = Depends(lister_decisions),
) -> PageRegistre:
    agence_id = user.agence_id if user.role == "agent" else None
    decisions, total = use_case.execute(agence_id, limite, decalage)
    return PageRegistre(elements=[mappers.decision_to_registre(d) for d in decisions], total=total)
