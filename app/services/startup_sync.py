from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.config import settings
from app.services.catalog_sync import sync_catalog
from app.services.preset_service import sync_presets

logger = logging.getLogger(__name__)


def sync_source_files(session: Session) -> tuple[int, int]:
    """Sync catalog and presets into local SQLite cache."""
    catalog_count = sync_catalog(session, settings.catalog_path)
    preset_count = sync_presets(session, settings.presets_path)
    logger.info("Startup sync complete", extra={"catalog_count": catalog_count, "preset_count": preset_count})
    return catalog_count, preset_count
