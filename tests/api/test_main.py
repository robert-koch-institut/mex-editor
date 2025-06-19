import pytest
from fastapi.testclient import TestClient

from mex.common.testing import Joker


@pytest.mark.integration
def test_health_check(client: TestClient) -> None:
    response = client.get("/_system/check")
    assert response.status_code == 200, response.text
    assert response.json() == {"status": "ok", "version": Joker()}


@pytest.mark.integration
@pytest.mark.usefixtures("load_dummy_data")
def test_prometheus_metrics(client: TestClient) -> None:
    response = client.get("/_system/metrics")
    assert response.status_code == 200, response.text
    assert response.text == (
        """\
# TYPE backend_api_identity_provider_cache_hits counter
backend_api_identity_provider_cache_hits 18

# TYPE backend_api_identity_provider_cache_misses counter
backend_api_identity_provider_cache_misses 7"""
    )
