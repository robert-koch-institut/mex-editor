from typing import TYPE_CHECKING

from starlette import status

if TYPE_CHECKING:  # pragma: no cover
    from fastapi.testclient import TestClient


def test_list_vocabularies(client: TestClient) -> None:
    response = client.get("/api/v0/vocabulary")
    assert response.status_code == status.HTTP_200_OK, response.text
    names = response.json()
    assert isinstance(names, list)
    assert "bibliographic-resource-type" in names
    assert len(names) == 17


def test_get_vocabulary(client: TestClient) -> None:
    response = client.get("/api/v0/vocabulary/bibliographic-resource-type")
    assert response.status_code == status.HTTP_200_OK, response.text
    container = response.json()
    assert set(container) == {"items", "total"}
    assert container["total"] == len(container["items"])
    assert container["items"]
    first = container["items"][0]
    assert "identifier" in first
    assert set(first["prefLabel"]) == {"de", "en"}


def test_get_vocabulary_unknown(client: TestClient) -> None:
    response = client.get("/api/v0/vocabulary/does-not-exist")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
