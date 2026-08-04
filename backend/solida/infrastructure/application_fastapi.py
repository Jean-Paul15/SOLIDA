from fastapi import FastAPI

from solida.adapters.http.routeurs import sante


def creer_application() -> FastAPI:
    application = FastAPI(title="SOLIDA API")
    application.include_router(sante.routeur)
    return application


app = creer_application()
