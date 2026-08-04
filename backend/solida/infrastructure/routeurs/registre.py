from fastapi import APIRouter, Depends

from solida.adapters.http import mappers
from solida.adapters.http.schemas.registre import PageRegistre
from solida.adapters.persistence.modeles_sqlalchemy import Utilisateur
from solida.application.use_cases.lister_decisions import ListerDecisions
from solida.infrastructure.auth import current_active_user
from solida.infrastructure.dependances import lister_decisions

routeur = APIRouter(prefix="/api/v1/registre", tags=["registre"])


@routeur.get("", response_model=PageRegistre)
def lister(
    limite: int = 20,
    decalage: int = 0,
    utilisateur: Utilisateur = Depends(current_active_user),
    cas_usage: ListerDecisions = Depends(lister_decisions),
) -> PageRegistre:
    agence_id = utilisateur.agence_id if utilisateur.role == "agent" else None
    decisions, total = cas_usage.executer(agence_id, limite, decalage)
    return PageRegistre(
        elements=[mappers.decision_vers_registre(d) for d in decisions], total=total
    )
