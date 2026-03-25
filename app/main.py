import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db import Base, SessionLocal, engine
from app.routes.web import router as web_router
from app.services.startup_sync import sync_source_files

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.startup_error = None
    with SessionLocal() as session:
        try:
            sync_source_files(session)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to sync source files during startup")
            app.state.startup_error = (
                "Unable to load source files. Please check catalog.xlsx and presets.json. "
                f"Details: {exc}"
            )
    yield


def create_app() -> FastAPI:
    settings.local_data_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="MedMatrix", lifespan=lifespan)
    app.state.session_store = {}
    app.add_middleware(SessionMiddleware, secret_key="dev-secret-change-me")
    app.include_router(web_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    return app


app = create_app()
