import reflex as rx

from mex.editor.edit.main import index as edit_index
from mex.editor.merge.main import index as merge_index
from mex.editor.search.main import index as search_index
from mex.main import check_system_status

app = rx.App()
app.add_page(edit_index, route="/item/[item_id]", title="MEx Editor | Edit")
app.add_page(merge_index, route="/merge", title="MEx Editor | Merge")
app.add_page(search_index, route="/", title="MEx Editor | Search")
app.api.add_api_route("/_system/check", check_system_status, tags=["system"])
