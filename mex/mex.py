import reflex as rx
from fastapi.responses import PlainTextResponse
from reflex.app import UnevaluatedPage
from reflex.components.core.client_side_routing import Default404Page
from reflex.components.radix import themes
from reflex.constants import Page404
from reflex.utils.console import info as log_info

from mex.common.logging import logger
from mex.editor.api.main import check_system_status, get_prometheus_metrics
from mex.editor.consent.main import index as consent_index
from mex.editor.consent.state import ConsentState
from mex.editor.create.main import index as create_index
from mex.editor.create.state import CreateState
from mex.editor.edit.main import index as edit_index
from mex.editor.edit.state import EditState
from mex.editor.ingest.main import index as ingest_index
from mex.editor.ingest.state import IngestState
from mex.editor.login.main import ldap_login as login_ldap_index
from mex.editor.login.main import mex_login as login_mex_index
from mex.editor.merge.main import index as merge_index
from mex.editor.merge.state import MergeState
from mex.editor.rules.state import RuleState
from mex.editor.search.main import index as search_index
from mex.editor.search.state import SearchState
from mex.editor.settings import EditorSettings
from mex.editor.state import State

app = rx.App(
    html_lang="en",
    theme=themes.theme(accent_color="blue", has_background=False),
    style={">a": {"opacity": "0"}},
)
app.add_page(
    search_index,
    route="/",
    title="MEx Editor | Search",
    on_load=[
        State.check_mex_login,
        State.load_nav,
        SearchState.get_available_primary_sources,
        SearchState.load_search_params,
        SearchState.refresh,
        SearchState.resolve_identifiers,
    ],
)
app.add_page(
    merge_index,
    route="/merge",
    title="MEx Editor | Merge",
    on_load=[
        State.check_mex_login,
        State.load_nav,
        MergeState.refresh,
        MergeState.resolve_identifiers,
    ],
)
app.add_page(
    create_index,
    route="/create",
    title="MEx Editor | Create",
    on_load=[
        State.check_mex_login,
        State.load_nav,
        CreateState.reset_stem_type,
        RuleState.refresh,
        RuleState.resolve_identifiers,
    ],
)
app.add_page(
    edit_index,
    route="/item/[identifier]",
    title="MEx Editor | Edit",
    on_load=[
        State.check_mex_login,
        State.load_nav,
        RuleState.refresh,
        EditState.load_item_title,
        EditState.show_submit_success_toast_on_redirect,
        RuleState.resolve_identifiers,
    ],
)
app.add_page(
    ingest_index,
    route="/ingest",
    title="MEx Editor | Ingest",
    on_load=[
        State.check_mex_login,
        State.load_nav,
        IngestState.refresh,
        IngestState.resolve_identifiers,
    ],
)
app.add_page(
    login_mex_index,
    route="/login",
    title="MEx Editor | Login",
)
app.add_page(
    login_ldap_index,
    route="/login-ldap",
    title="MEx Editor | Login",
)
app.add_page(
    consent_index,
    route="/consent",
    title="MEx Consent",
    on_load=[
        State.check_ldap_login,
        ConsentState.load_user,
    ],
)
# side-step `add_page` to avoid `wait_for_client_redirect`,
# because that breaks deployment behind a base path.
app.unevaluated_pages[Page404.SLUG] = UnevaluatedPage(
    component=Default404Page.create(),
    route=Page404.SLUG,
    title=Page404.TITLE,
    description=Page404.DESCRIPTION,
    image=Page404.IMAGE,
    on_load=None,
    meta=[],
)
app.api.add_api_route(
    "/_system/check",
    check_system_status,
    tags=["system"],
)
app.api.add_api_route(
    "/_system/metrics",
    get_prometheus_metrics,
    response_class=PlainTextResponse,
    tags=["system"],
)
app.api.title = "mex-editor"
app.api.version = "v0"
app.api.contact = {"name": "MEx Team", "email": "mex@rki.de"}
app.api.description = "Metadata editor web application."

app.register_lifespan_task(
    lambda: logger.info(EditorSettings.get().text()),
)
app.register_lifespan_task(
    log_info,
    msg="MEx Editor is running, shut it down using CTRL+C",
)
