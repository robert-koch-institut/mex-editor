from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/_system/check")
    assert response.status_code == 200, response.text
    assert response.json() == {"status": "ok"}
