from __future__ import annotations

import base64

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import MedicationCatalog
from app.services.datamatrix_service import render_data_matrix_png
from app.services.payload_builder import SelectedItem, build_payload
from app.services.selection_state import group_selection

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    medications = session.scalars(
        select(MedicationCatalog)
        .where(MedicationCatalog.is_active.is_(True))
        .order_by(MedicationCatalog.product_class, MedicationCatalog.sort_order, MedicationCatalog.product_name)
    ).all()
    selected = request.session.get("selection", [])
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "medications": medications,
            "grouped_selection": group_selection(selected),
            "barcode_b64": request.session.get("barcode_b64"),
            "payload": request.session.get("payload", ""),
        },
    )


@router.post("/generate", response_class=HTMLResponse)
def generate(request: Request, session: Session = Depends(get_session), item_ids: list[int] = Form(default=[])):
    meds = session.scalars(select(MedicationCatalog).where(MedicationCatalog.id.in_(item_ids))).all() if item_ids else []
    selected = [
        {
            "id": m.id,
            "product_class": m.product_class,
            "product_name": m.product_name,
            "unique_id": m.unique_id,
            "quantity": 1,
        }
        for m in meds
    ]
    request.session["selection"] = selected

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
    request.session["payload"] = payload
    request.session["barcode_b64"] = (
        base64.b64encode(render_data_matrix_png(payload)).decode("ascii") if payload else None
    )
    return index(request, session)
