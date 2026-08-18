from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/v1/health")
def read_health() -> dict[str, str]:
    return {"statut": "ok"}
