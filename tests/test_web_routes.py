from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import create_app
from app.db import engine
from app.models import MedicationCatalog


def test_index_route_renders_page():
    app = create_app()
    with Session(engine) as session:
        session.add(MedicationCatalog(product_class="Induction", product_name="Propofol", unique_id="P001"))
        session.commit()

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "MedMatrix" in response.text
