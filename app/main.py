from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db import Base, engine
from app.routes.web import router as web_router


def create_app() -> FastAPI:
    settings.local_data_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="MedMatrix")
    app.add_middleware(SessionMiddleware, secret_key="dev-secret-change-me")
    app.include_router(web_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    return app


app = create_app()
