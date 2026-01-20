from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from mex.editor.ingest.state import IngestState
from mex.editor.pagination_component import (
    PaginationButtonOptions,
    PaginationOptions,
    PaginationPageOptions,
)
from mex.editor.search.state import SearchState

if TYPE_CHECKING:
    from reflex import Var


def build_pagination_options(
    state: type[IngestState | SearchState], *page_load_hooks: Callable[[], Any]
) -> PaginationOptions:
    """Build pagination options for IngestState or SearchState."""
    current_page = cast("Var[int]", state.current_page)
    return PaginationOptions(
        PaginationButtonOptions(
            state.disable_previous_page,
            [
                state.go_to_previous_page,
                state.scroll_to_top,
                state.refresh,
                state.resolve_identifiers,
                *page_load_hooks,
            ],
        ),
        PaginationButtonOptions(
            state.disable_next_page,
            [
                state.go_to_next_page,
                state.scroll_to_top,
                state.refresh,
                state.resolve_identifiers,
                *page_load_hooks,
            ],
        ),
        PaginationPageOptions(
            current_page,
            state.page_selection,
            state.disable_page_selection,
            [
                state.set_current_page,
                state.scroll_to_top,
                state.refresh,
                state.resolve_identifiers,
                *page_load_hooks,
            ],
        ),
    )
