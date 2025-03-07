import pytest
from fastapi.testclient import TestClient
from playwright.sync_api import Page, expect
from pydantic import SecretStr
from pytest import MonkeyPatch

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AnyExtractedModel,
    AnyRuleSetResponse,
    ExtractedActivity,
    ExtractedContactPoint,
    ExtractedOrganizationalUnit,
    ExtractedPrimarySource,
)
from mex.common.types import (
    Email,
    IdentityProvider,
    Link,
    Text,
    TextLanguage,
    Theme,
    YearMonthDay,
)
from mex.editor.settings import EditorSettings
from mex.editor.types import EditorUserDatabase, EditorUserPassword
from mex.mex import app

pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    with TestClient(app.api, raise_server_exceptions=False) as test_client:
        return test_client


@pytest.fixture(autouse=True)
def settings() -> EditorSettings:
    """Load and return the current editor settings."""
    return EditorSettings.get()


@pytest.fixture(autouse=True)
def set_identity_provider(is_integration_test: bool, monkeypatch: MonkeyPatch) -> None:
    """Ensure the identifier provider is set correctly for unit and int tests."""
    # TODO(ND): clean this up after MX-1708
    settings = EditorSettings.get()
    if is_integration_test:
        monkeypatch.setitem(settings.model_config, "validate_assignment", False)
        monkeypatch.setattr(settings, "identity_provider", IdentityProvider.BACKEND)
    else:
        monkeypatch.setattr(settings, "identity_provider", IdentityProvider.MEMORY)


@pytest.fixture
def frontend_url() -> str:
    """Return the URL of the current local frontend server for testing."""
    return "http://localhost:3000"


@pytest.fixture(autouse=True)
def patch_editor_user_database(
    is_integration_test: bool, monkeypatch: MonkeyPatch, settings: EditorSettings
) -> None:
    """Overwrite the user database with dummy credentials."""
    if not is_integration_test:
        monkeypatch.setattr(
            settings,
            "editor_user_database",
            EditorUserDatabase(
                read={"reader": EditorUserPassword("reader_pass")},
                write={"writer": EditorUserPassword("writer_pass")},
            ),
        )


@pytest.fixture
def writer_user_credentials() -> tuple[str, SecretStr]:
    settings = EditorSettings.get()
    for username, password in settings.editor_user_database["write"].items():
        return username, password
    msg = "No writer configured"  # pragma: no cover
    raise RuntimeError(msg)  # pragma: no cover


def login_user(
    frontend_url: str, page: Page, username: str, password: SecretStr
) -> Page:
    page.goto(frontend_url)
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password.get_secret_value())
    page.get_by_test_id("login-button").click()
    return page


@pytest.fixture
def writer_user_page(
    page: Page, writer_user_credentials: tuple[str, SecretStr], frontend_url: str
) -> Page:
    login_user(frontend_url, page, *writer_user_credentials)
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    return page


@pytest.fixture(autouse=True)
def flush_graph_database(is_integration_test: bool) -> None:
    """Flush the graph database before every integration test."""
    if is_integration_test:
        connector = BackendApiConnector.get()
        # TODO(ND): use proper connector method when available (stopgap mx-1762)
        connector.request(method="DELETE", endpoint="/_system/graph")


@pytest.fixture
def dummy_data() -> list[AnyExtractedModel]:
    """Create a set of interlinked dummy data."""
    primary_source_1 = ExtractedPrimarySource(
        hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        identifierInPrimarySource="ps-1",
    )
    primary_source_2 = ExtractedPrimarySource(
        hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        identifierInPrimarySource="ps-2",
        version="Cool Version v2.13",
    )
    contact_point_1 = ExtractedContactPoint(
        email=[Email("info@contact-point.one")],
        hadPrimarySource=primary_source_1.stableTargetId,
        identifierInPrimarySource="cp-1",
    )
    contact_point_2 = ExtractedContactPoint(
        email=[Email("help@contact-point.two")],
        hadPrimarySource=primary_source_1.stableTargetId,
        identifierInPrimarySource="cp-2",
    )
    organizational_unit_1 = ExtractedOrganizationalUnit(
        hadPrimarySource=primary_source_2.stableTargetId,
        identifierInPrimarySource="ou-1",
        name=[Text(value="Unit 1", language=TextLanguage.EN)],
        shortName=["OU1"],
    )
    activity_1 = ExtractedActivity(
        abstract=[
            Text(value="An active activity.", language=TextLanguage.EN),
            Text(value="Une activité active.", language=None),
        ],
        contact=[
            contact_point_1.stableTargetId,
            contact_point_2.stableTargetId,
            organizational_unit_1.stableTargetId,
        ],
        hadPrimarySource=primary_source_1.stableTargetId,
        identifierInPrimarySource="a-1",
        responsibleUnit=[organizational_unit_1.stableTargetId],
        shortName=["A1"],
        start=[YearMonthDay(1999, 12, 24)],
        end=[YearMonthDay(2023, 1, 1)],
        theme=[Theme["INFECTIOUS_DISEASES_AND_EPIDEMIOLOGY"]],
        title=[Text(value="Aktivität 1", language=TextLanguage.DE)],
        website=[Link(title="Activity Homepage", url="https://activity-1")],
    )
    return [
        primary_source_1,
        primary_source_2,
        contact_point_1,
        contact_point_2,
        organizational_unit_1,
        activity_1,
    ]


@pytest.fixture
def load_dummy_data(
    dummy_data: list[AnyExtractedModel | AnyRuleSetResponse],
    flush_graph_database: None,  # noqa: ARG001
) -> list[AnyExtractedModel | AnyRuleSetResponse]:
    """Ingest dummy data into the backend."""
    connector = BackendApiConnector.get()
    return connector.ingest(dummy_data)
