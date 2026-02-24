from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_encode_simple():
    response = client.post("/encode", json={"text": "こんにちは"})
    assert response.status_code == 200
    data = response.json()
    assert "vectors" in data
    assert isinstance(data["vectors"], dict)
    # SPLADE should return some sparse features
    assert len(data["vectors"]) > 0


def test_encode_empty():
    response = client.post("/encode", json={"text": ""})
    assert response.status_code == 200
    assert response.json() == {"vectors": {}}
