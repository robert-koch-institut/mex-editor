from contextlib import closing

import pytest
from fastapi.testclient import TestClient
from playwright.sync_api import Page, expect
from pydantic import SecretStr
from pytest import MonkeyPatch

from mex.backend.graph.connector import GraphConnector
from mex.backend.graph.models import Result
from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import (
    EXTRACTED_MODEL_CLASSES,
    MERGED_MODEL_CLASSES,
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AnyExtractedModel,
    ExtractedActivity,
    ExtractedContactPoint,
    ExtractedOrganizationalUnit,
    ExtractedPrimarySource,
)
from mex.common.settings import SETTINGS_STORE
from mex.common.types import (
    Email,
    Identifier,
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


@pytest.fixture
def reader_user_credentials() -> tuple[str, SecretStr]:
    settings = EditorSettings.get()
    for username, password in settings.editor_user_database["read"].items():
        return username, password
    raise RuntimeError("No reader configured")  # pragma: no cover


@pytest.fixture
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


@pytest.fixture
def reader_user_page(
    page: Page,
    reader_user_credentials: tuple[str, SecretStr],
) -> Page:
    login_user(page, *reader_user_credentials)
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    return page


@pytest.fixture
def writer_user_page(
    page: Page,
    writer_user_credentials: tuple[str, SecretStr],
) -> Page:
    login_user(page, *writer_user_credentials)
    expect(page.get_by_test_id("nav-bar")).to_be_visible()
    return page


class ResettingGraphConnector(GraphConnector):
    def _seed_constraints(self) -> list[Result]:
        for row in self.commit("SHOW ALL CONSTRAINTS;").all():
            self.commit(f"DROP CONSTRAINT {row['name']};")
        return super()._seed_constraints()

    def _seed_indices(self) -> Result:
        for row in self.commit("SHOW ALL INDEXES WHERE type = 'FULLTEXT';").all():
            self.commit(f"DROP INDEX {row['name']};")
        return super()._seed_indices()

    def _seed_data(self) -> list[Identifier]:
        self.commit("MATCH (n) DETACH DELETE n;")
        return super()._seed_data()


@pytest.fixture(autouse=True)
def isolate_graph_database(settings: EditorSettings, is_integration_test: bool) -> None:
    """Rebuild the graph in a sub-process, so the settings won't get angry with us."""
    if is_integration_test:
        SETTINGS_STORE.reset()
        with closing(ResettingGraphConnector()) as connector:
            assert connector.commit(
                "SHOW ALL CONSTRAINTS YIELD id RETURN COUNT(id) AS total;"
            )["total"] == (len(EXTRACTED_MODEL_CLASSES) + len(MERGED_MODEL_CLASSES))
            assert (
                connector.commit("SHOW ALL INDEXES WHERE type = 'FULLTEXT';")["name"]
                == "search_index"
            )
            assert connector.commit("MATCH (n) RETURN COUNT(n) AS total;")["total"] == 2
        SETTINGS_STORE.push(settings)


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
def load_dummy_data(dummy_data: list[AnyExtractedModel]) -> list[AnyExtractedModel]:
    """Ingest dummy data into the backend."""
    connector = BackendApiConnector.get()
    connector.post_extracted_items(dummy_data)
    return dummy_data
