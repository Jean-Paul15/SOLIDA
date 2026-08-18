from fastapi import APIRouter, Depends

from solida.adapters.http import mappers
from solida.adapters.http.auth_dependencies import current_active_user
from solida.adapters.http.schemas.produits import ProduitCredit
from solida.adapters.persistence.modeles_sqlalchemy import Utilisateur
from solida.application.use_cases.lister_produits import ListerProduits
from solida.infrastructure.dependances import lister_produits

router = APIRouter(prefix="/api/v1/produits", tags=["produits"])


@router.get("", response_model=list[ProduitCredit])
def lister(
    utilisateur: Utilisateur = Depends(current_active_user),
    cas_usage: ListerProduits = Depends(lister_produits),
) -> list[ProduitCredit]:
    return [mappers.produit_vers_schema(p) for p in cas_usage.executer()]
