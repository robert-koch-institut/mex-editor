from typing import Any

import pytest
from fastapi.testclient import TestClient
from playwright.sync_api import Page, expect
from pydantic import SecretStr
from pytest import MonkeyPatch

from mex.artificial.helpers import generate_artificial_extracted_items
from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import (
    EXTRACTED_MODEL_CLASSES_BY_NAME,
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AnyExtractedModel,
    ExtractedActivity,
    ExtractedContactPoint,
    ExtractedOrganizationalUnit,
    ExtractedPrimarySource,
    ExtractedResource,
)
from mex.common.types import (
    AccessRestriction,
    Email,
    Identifier,
    IdentityProvider,
    Link,
    Text,
    TextLanguage,
    Theme,
    YearMonthDay,
)
from mex.editor.api.main import api
from mex.editor.settings import EditorSettings
from mex.editor.types import EditorUserDatabase, EditorUserPassword

pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any],
) -> dict[str, Any]:
    """Run the playwright test browser in a larger resolution than its default."""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1600,
            "height": 900,
        },
    }


@pytest.fixture
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    with TestClient(api, raise_server_exceptions=False) as test_client:
        return test_client


@pytest.fixture(autouse=True)
def settings() -> EditorSettings:
    """Load and return the current editor settings."""
    return EditorSettings.get()


@pytest.fixture(autouse=True)
def set_identity_provider(
    is_integration_test: bool,  # noqa: FBT001
    monkeypatch: MonkeyPatch,
) -> None:
    """Ensure the identifier provider is set correctly for unit and int tests."""
    # TODO(ND): clean this up after MX-1708
    settings = EditorSettings.get()
    if is_integration_test:
        monkeypatch.setitem(settings.model_config, "validate_assignment", False)  # noqa: FBT003
        monkeypatch.setattr(settings, "identity_provider", IdentityProvider.BACKEND)
    else:
        monkeypatch.setattr(settings, "identity_provider", IdentityProvider.MEMORY)


@pytest.fixture
def frontend_url() -> str:
    """Return the URL of the current local frontend server for testing."""
    return "http://localhost:3000"


@pytest.fixture(autouse=True)
def patch_editor_user_database(
    is_integration_test: bool,  # noqa: FBT001
    monkeypatch: MonkeyPatch,
    settings: EditorSettings,
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
    page.set_default_navigation_timeout(50_000)
    page.set_default_timeout(15_000)
    expect.set_options(timeout=15_000)
    return page


@pytest.fixture(autouse=True)
def flush_graph_database(is_integration_test: bool) -> None:  # noqa: FBT001
    """Flush the graph database before every integration test."""
    if is_integration_test:
        connector = BackendApiConnector.get()
        # TODO(ND): use proper connector method when available (stopgap mx-1984)
        connector.request(method="DELETE", endpoint="/_system/graph")


@pytest.fixture
def dummy_data() -> list[AnyExtractedModel]:
    """Create a set of interlinked dummy data."""
    primary_source_1 = ExtractedPrimarySource(
        hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        identifierInPrimarySource="ps-1",
        title=[Text(value="Primary Source One", language=TextLanguage.EN)],
    )
    primary_source_2 = ExtractedPrimarySource(
        hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        identifierInPrimarySource="ps-2",
        version="Cool Version v2.13",
        title=[Text(value="Primary Source Two", language=TextLanguage.EN)],
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
        website=[
            Link(title="Activity Homepage", url="https://activity-1"),
            Link(url="https://activity-homepage-1"),
        ],
    )
    resource_1 = ExtractedResource(
        hadPrimarySource=primary_source_1.stableTargetId,
        identifierInPrimarySource="r-1",
        accessRestriction=AccessRestriction["OPEN"],
        contact=[contact_point_1.stableTargetId],
        theme=[Theme["BIOINFORMATICS_AND_SYSTEMS_BIOLOGY"]],
        title=[Text(value="Bioinformatics Resource 1", language=None)],
        unitInCharge=[organizational_unit_1.stableTargetId],
    )
    resource_2 = ExtractedResource(
        hadPrimarySource=primary_source_2.stableTargetId,
        identifierInPrimarySource="r-2",
        accessRestriction=AccessRestriction["OPEN"],
        contact=[contact_point_1.stableTargetId, contact_point_2.stableTargetId],
        theme=[Theme["PUBLIC_HEALTH"]],
        title=[
            Text(value="Some Resource with many titles 1", language=None),
            Text(value="Some Resource with many titles 2", language=TextLanguage.EN),
            Text(value="Eine Resource mit vielen Titeln 3", language=TextLanguage.DE),
            Text(value="Some Resource with many titles 4", language=None),
        ],
        unitInCharge=[organizational_unit_1.stableTargetId],
    )
    return [
        primary_source_1,
        primary_source_2,
        contact_point_1,
        contact_point_2,
        organizational_unit_1,
        activity_1,
        resource_1,
        resource_2,
    ]


@pytest.fixture
def dummy_data_by_identifier_in_primary_source(
    dummy_data: list[AnyExtractedModel],
) -> dict[str, AnyExtractedModel]:
    return {model.identifierInPrimarySource: model for model in dummy_data}


@pytest.fixture
def dummy_data_by_stable_target_id(
    dummy_data: list[AnyExtractedModel],
) -> dict[Identifier, AnyExtractedModel]:
    return {model.stableTargetId: model for model in dummy_data}


@pytest.fixture
def load_dummy_data(
    dummy_data: list[AnyExtractedModel],
    flush_graph_database: None,  # noqa: ARG001
) -> None:
    """Ingest dummy data into the backend."""
    connector = BackendApiConnector.get()
    connector.ingest(dummy_data)


@pytest.fixture
def load_pagination_dummy_data(
    dummy_data: list[AnyExtractedModel],
    flush_graph_database: None,  # noqa: ARG001
) -> None:
    """Ingest dummy data into the backend."""
    connector = BackendApiConnector.get()
    primary_source_1 = next(
        x for x in dummy_data if x.identifierInPrimarySource == "ps-1"
    )

    pagination_dummy_data = []
    pagination_dummy_data.extend(dummy_data)
    pagination_dummy_data.extend(
        [
            ExtractedContactPoint(
                email=[Email(f"help-{i}@pagination.abc")],
                hadPrimarySource=primary_source_1.stableTargetId,
                identifierInPrimarySource=f"cp-pagination-test-{i}",
            )
            for i in range(100)
        ]
    )
    connector.ingest(pagination_dummy_data)


@pytest.fixture
def extracted_activity(
    dummy_data_by_identifier_in_primary_source: dict[str, AnyExtractedModel],
) -> ExtractedActivity:
    extracted_activity = dummy_data_by_identifier_in_primary_source["a-1"]
    assert type(extracted_activity) is ExtractedActivity
    return extracted_activity


@pytest.fixture
def artificial_extracted_items() -> list[AnyExtractedModel]:
    return generate_artificial_extracted_items(
        locale="de_DE",
        seed=42,
        count=25,
        chattiness=16,
        stem_types=list(EXTRACTED_MODEL_CLASSES_BY_NAME),
    )


@pytest.fixture
def load_artificial_extracted_items(
    artificial_extracted_items: list[AnyExtractedModel],
) -> list[AnyExtractedModel]:
    """Ingest artificial data into the graph."""
    connector = BackendApiConnector.get()
    connector.ingest(artificial_extracted_items)
    return artificial_extracted_items
