from typing import TYPE_CHECKING

from starlette import status

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_get_vocabulary(client: TestClient) -> None:
    response = client.get("/api/v0/vocabulary/bibliographic-resource-type")
    assert response.status_code == status.HTTP_200_OK, response.text
    concepts = response.json()
    assert concepts
    assert concepts[0] == {
        "identifier": "https://mex.rki.de/item/bibliographic-resource-type-1",
        "prefLabel": {"de": "Buch", "en": "Book"},
        "altLabel": [{"de": "Monografie", "en": "Monograph"}],
    }


def test_get_vocabulary_unknown(client: TestClient) -> None:
    response = client.get("/api/v0/vocabulary/does-not-exist")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
