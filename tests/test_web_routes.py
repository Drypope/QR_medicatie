import pytest
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import engine
from app.main import create_app
from app.models import MedicationCatalog, Preset, PresetItem


def _seed_catalog_and_preset() -> tuple[int, int, int, str, str]:
    suffix = uuid4().hex[:8]
    with Session(engine) as session:
        med_a = MedicationCatalog(
            product_class="TestClass",
            product_name=f"Test Med A {suffix}",
            unique_id=f"TMA{suffix}",
            is_active=True,
        )
        med_b = MedicationCatalog(
            product_class="TestClass",
            product_name=f"Test Med B {suffix}",
            unique_id=f"TMB{suffix}",
            is_active=True,
        )
        session.add_all([med_a, med_b])
        session.flush()

        preset = Preset(name=f"Test Preset {suffix}", description="test")
        session.add(preset)
        session.flush()

        session.add(PresetItem(preset_id=preset.id, catalog_id=med_a.id, default_quantity=2))
        session.commit()
        return med_a.id, med_b.id, preset.id, med_a.unique_id, med_b.unique_id


@pytest.fixture
def datamatrix_stub(monkeypatch):
    monkeypatch.setattr("app.routes.web.render_data_matrix_png", lambda payload: b"PNG")


def test_index_route_renders_page(datamatrix_stub):
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "MEDICATIETOOL" in response.text


def test_selection_routes_and_generate_use_session_selection(datamatrix_stub):
    med_a_id, med_b_id, _preset_id, med_a_uid, med_b_uid = _seed_catalog_and_preset()
    app = create_app()

    with TestClient(app) as client:
        assert client.post("/selection/add-item", data={"catalog_id": med_a_id}).status_code == 200
        assert client.post("/selection/increment", data={"catalog_id": med_a_id}).status_code == 200
        assert client.post("/selection/decrement", data={"catalog_id": med_a_id}).status_code == 200

        assert client.post("/selection/add-item", data={"catalog_id": med_b_id}).status_code == 200
        assert client.post("/selection/delete", data={"catalog_id": med_b_id}).status_code == 200

        generated = client.post("/generate")

    assert generated.status_code == 200
    assert f"$2037--{med_a_uid}" in generated.text
    assert med_b_uid not in generated.text


def test_load_preset_route_loads_session_selection(datamatrix_stub):
    _med_a_id, _med_b_id, preset_id, med_a_uid, _med_b_uid = _seed_catalog_and_preset()
    app = create_app()

    with TestClient(app) as client:
        loaded = client.post("/selection/load-preset", data={"preset_id": preset_id})
        generated = client.post("/generate")

    assert loaded.status_code == 200
    assert generated.status_code == 200
    assert generated.text.count(f"$2037--{med_a_uid}") == 2


def test_admin_refresh_route_shows_success(datamatrix_stub, monkeypatch):
    app = create_app()
    monkeypatch.setattr("app.routes.web.sync_source_files", lambda session: (5, 2))

    with TestClient(app) as client:
        response = client.post("/admin/refresh")

    assert response.status_code == 200
    assert "Refresh complete" in response.text


def test_admin_refresh_route_shows_friendly_error(datamatrix_stub, monkeypatch):
    app = create_app()

    def _raise(_session):
        raise FileNotFoundError("Catalog file not found")

    monkeypatch.setattr("app.routes.web.sync_source_files", _raise)

    with TestClient(app) as client:
        response = client.post("/admin/refresh")

    assert response.status_code == 200
    assert "Refresh failed" in response.text
    assert "catalog.xlsx" in response.text
