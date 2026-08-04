from fastapi import APIRouter

routeur = APIRouter(tags=["sante"])


@routeur.get("/api/v1/sante")
def lire_sante() -> dict[str, str]:
    return {"statut": "ok"}
