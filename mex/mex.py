import reflex as rx
from reflex.components.radix import themes
from reflex.utils.console import info as log_info

from mex.common.logging import logger
from mex.editor.api.main import check_system_status
from mex.editor.edit.main import index as edit_index
from mex.editor.login.main import index as login_index
from mex.editor.merge.main import index as merge_index
from mex.editor.search.main import index as search_index
from mex.editor.settings import EditorSettings
from mex.editor.state import State

app = rx.App(
    html_lang="en",
    theme=themes.theme(accent_color="blue"),
)
app.add_page(
    edit_index,
    route="/item/[item_id]",
    title="MEx Editor | Edit",
    on_load=State.check_login,
)
app.add_page(
    merge_index,
    route="/merge",
    title="MEx Editor | Merge",
    on_load=State.check_login,
)
app.add_page(
    search_index,
    route="/",
    title="MEx Editor | Search",
    on_load=State.check_login,
)
app.add_page(
    login_index,
    route="/login",
    title="MEx Editor | Login",
)
app.api.add_api_route(
    "/_system/check",
    check_system_status,
    tags=["system"],
)
app.register_lifespan_task(
    log_info,
    msg="MEx Editor is running, shut it down using CTRL+C",
)
app.register_lifespan_task(lambda: logger.info(EditorSettings.get().text()))
