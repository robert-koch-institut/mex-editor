import pytest
from fastapi.testclient import TestClient
from neo4j import GraphDatabase
from playwright.sync_api import Page, expect
from pydantic import Field, SecretStr
from pytest import MonkeyPatch

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AnyExtractedModel,
    ExtractedActivity,
    ExtractedContactPoint,
    ExtractedOrganizationalUnit,
    ExtractedPrimarySource,
)
from mex.common.settings import BaseSettings
from mex.common.types import Email, Link, Text, TextLanguage, Theme, YearMonthDay
from mex.editor.settings import EditorSettings
from mex.editor.types import EditorUserDatabase, EditorUserPassword
from mex.mex import app

pytest_plugins = ("mex.common.testing.plugin",)


@pytest.fixture()
def client() -> TestClient:
    """Return a fastAPI test client initialized with our app."""
    with TestClient(app.api, raise_server_exceptions=False) as test_client:
        return test_client


@pytest.fixture(autouse=True)
def settings() -> EditorSettings:
    return EditorSettings.get()


@pytest.fixture(autouse=True)
def patch_editor_user_database(
    is_integration_test: bool, monkeypatch: MonkeyPatch, settings: EditorSettings
) -> None:
    if not is_integration_test:
        monkeypatch.setattr(
            settings,
            "editor_user_database",
            EditorUserDatabase(
                read={"reader": EditorUserPassword("reader_pass")},
                write={"writer": EditorUserPassword("writer_pass")},
            ),
        )


@pytest.fixture()
def reader_user_credentials() -> tuple[str, SecretStr]:
    settings = EditorSettings.get()
    for username, password in settings.editor_user_database["read"].items():
        return username, password
    raise RuntimeError("No reader configured")  # pragma: no cover


@pytest.fixture()
def writer_user_credentials() -> tuple[str, SecretStr]:
    settings = EditorSettings.get()
    for username, password in settings.editor_user_database["write"].items():
        return username, password
    raise RuntimeError("No writer configured")  # pragma: no cover


def login_user(page: Page, username: str, password: SecretStr) -> Page:
    page.goto("http://localhost:3000")
    page.get_by_placeholder("Username").fill(username)
    page.get_by_placeholder("Password").fill(password.get_secret_value())
    page.get_by_text("Log in").click()
    return page


@pytest.fixture()
def reader_user_page(
    page: Page,
    reader_user_credentials: tuple[str, SecretStr],
) -> Page:
    login_user(page, *reader_user_credentials)
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    return page


@pytest.fixture()
def writer_user_page(
    page: Page,
    writer_user_credentials: tuple[str, SecretStr],
) -> Page:
    login_user(page, *writer_user_credentials)
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    return page


class GraphSettings(BaseSettings):
    graph_url: str = Field(
        "neo4j://localhost:7687",
        description="URL for connecting to the graph database.",
        validation_alias="MEX_GRAPH_URL",
    )
    graph_db: str = Field(
        "neo4j",
        description="Name of the default graph database.",
        validation_alias="MEX_GRAPH_NAME",
    )
    graph_user: SecretStr = Field(
        SecretStr("neo4j"),
        description="Username for authenticating with the graph database.",
        validation_alias="MEX_GRAPH_USER",
    )
    graph_password: SecretStr = Field(
        SecretStr("password"),
        description="Password for authenticating with the graph database.",
        validation_alias="MEX_GRAPH_PASSWORD",
    )


@pytest.fixture(autouse=True)
def isolate_graph_database(is_integration_test: bool) -> None:
    """Automatically flush the graph database for integration testing."""
    if is_integration_test:
        settings = GraphSettings()
        with GraphDatabase.driver(
            settings.graph_url,
            auth=(
                settings.graph_user.get_secret_value(),
                settings.graph_password.get_secret_value(),
            ),
            database=settings.graph_db,
        ) as driver:
            driver.execute_query("MATCH (n) DETACH DELETE n;")
            for row in driver.execute_query("SHOW ALL CONSTRAINTS;").records:
                driver.execute_query(f"DROP CONSTRAINT {row['name']};")
            for row in driver.execute_query("SHOW ALL INDEXES;").records:
                driver.execute_query(f"DROP INDEX {row['name']};")


@pytest.fixture()
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


@pytest.fixture()
def load_dummy_data(dummy_data: list[AnyExtractedModel]) -> list[AnyExtractedModel]:
    """Ingest dummy data into the backend."""
    connector = BackendApiConnector.get()
    connector.post_extracted_items(dummy_data)
    return dummy_data
