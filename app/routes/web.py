from __future__ import annotations

import base64
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import MedicationCatalog, Preset
from app.services.datamatrix_service import render_data_matrix_png
from app.services.payload_builder import SelectedItem, build_payload
from app.services.selection_service import add_catalog_item, load_preset_selection
from app.services.selection_state import (
    decrement_selected_item,
    delete_selected_item,
    get_selection,
    group_selected_by_product_class,
    increment_selected_item,
)
from app.services.startup_sync import sync_source_files

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _state(request: Request) -> dict:
    sid = request.session.get("sid")
    if not sid:
        sid = uuid4().hex
        request.session["sid"] = sid
    store = request.app.state.session_store
    return store.setdefault(sid, {})


def _render_index(request: Request, session: Session) -> HTMLResponse:
    state = _state(request)
    medications = session.scalars(
        select(MedicationCatalog)
        .where(MedicationCatalog.is_active.is_(True))
        .order_by(MedicationCatalog.product_class, MedicationCatalog.sort_order, MedicationCatalog.product_name)
    ).all()
    presets = session.scalars(select(Preset).order_by(Preset.name)).all()
    selected = get_selection(state)

    catalog_by_class: dict[str, list[dict[str, int | str]]] = {}
    for med in medications:
        catalog_by_class.setdefault(med.product_class, []).append({"id": med.id, "product_name": med.product_name})

    flash_error = state.pop("flash_error", None)
    flash_success = state.pop("flash_success", None)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "medications": medications,
            "presets": presets,
            "catalog_by_class": catalog_by_class,
            "grouped_selection": group_selected_by_product_class(selected),
            "barcode_b64": state.get("barcode_b64"),
            "payload": state.get("payload", ""),
            "flash_error": flash_error,
            "flash_success": flash_success,
            "startup_error": getattr(request.app.state, "startup_error", None),
        },
    )


@router.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    return _render_index(request, session)


@router.post("/admin/refresh", response_class=HTMLResponse)
def admin_refresh(request: Request, session: Session = Depends(get_session)):
    state = _state(request)
    try:
        catalog_count, preset_count = sync_source_files(session)
    except Exception as exc:  # noqa: BLE001
        state["flash_error"] = (
            "Refresh failed. Please verify catalog.xlsx and presets.json. "
            f"Details: {exc}"
        )
    else:
        state["flash_success"] = f"Refresh complete. Catalog rows: {catalog_count}, presets: {preset_count}."
        request.app.state.startup_error = None
    return _render_index(request, session)


@router.post("/selection/load-preset", response_class=HTMLResponse)
def load_preset(request: Request, preset_id: int = Form(...), session: Session = Depends(get_session)):
    state = _state(request)
    try:
        load_preset_selection(session, state, preset_id)
    except Exception as exc:  # noqa: BLE001
        state["flash_error"] = f"Unable to load preset. Details: {exc}"
    return _render_index(request, session)


@router.post("/selection/increment", response_class=HTMLResponse)
def increment_selection(request: Request, catalog_id: int = Form(...), session: Session = Depends(get_session)):
    increment_selected_item(_state(request), catalog_id)
    return _render_index(request, session)


@router.post("/selection/decrement", response_class=HTMLResponse)
def decrement_selection(request: Request, catalog_id: int = Form(...), session: Session = Depends(get_session)):
    decrement_selected_item(_state(request), catalog_id)
    return _render_index(request, session)


@router.post("/selection/delete", response_class=HTMLResponse)
def delete_selection(request: Request, catalog_id: int = Form(...), session: Session = Depends(get_session)):
    delete_selected_item(_state(request), catalog_id)
    return _render_index(request, session)


@router.post("/selection/add-item", response_class=HTMLResponse)
def add_selection_item(request: Request, catalog_id: int = Form(...), session: Session = Depends(get_session)):
    state = _state(request)
    try:
        add_catalog_item(session, state, catalog_id)
    except Exception as exc:  # noqa: BLE001
        state["flash_error"] = f"Unable to add medication. Details: {exc}"
    return _render_index(request, session)


@router.post("/generate", response_class=HTMLResponse)
def generate(request: Request, session: Session = Depends(get_session)):
    state = _state(request)
    selected = get_selection(state)

    payload = build_payload(
        [
            SelectedItem(
                unique_id=item["unique_id"],
                product_name=item["product_name"],
                quantity=int(item["quantity"]),
                product_class=item["product_class"],
            )
            for item in selected
        ]
    )
    state["payload"] = payload
    try:
        state["barcode_b64"] = (
            base64.b64encode(render_data_matrix_png(payload)).decode("ascii") if payload else None
        )
    except Exception as exc:  # noqa: BLE001
        state["flash_error"] = f"Barcode generation failed. Details: {exc}"
        state["barcode_b64"] = None
    return _render_index(request, session)
