from fastapi.testclient import TestClient

from app.main import create_app


def test_index_route_renders_page():
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "MedMatrix" in response.text
