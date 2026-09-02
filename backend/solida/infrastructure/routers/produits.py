from fastapi import APIRouter, Depends

from solida.adapters.http import mappers
from solida.adapters.http.schemas.produits import ProduitCredit
from solida.adapters.persistence.orm_models import User
from solida.application.use_cases.lister_produits import ListerProduits
from solida.infrastructure.auth.dependencies import current_active_user
from solida.infrastructure.dependencies import lister_produits

router = APIRouter(prefix="/api/v1/produits", tags=["produits"])


@router.get("", response_model=list[ProduitCredit])
def lister(
    user: User = Depends(current_active_user),
    use_case: ListerProduits = Depends(lister_produits),
) -> list[ProduitCredit]:
    return [mappers.produit_to_schema(p) for p in use_case.execute()]
