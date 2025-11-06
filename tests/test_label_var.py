from typing import TYPE_CHECKING, cast

import reflex as rx
from pytest import MonkeyPatch

from mex.editor.label_var import label_var
from mex.editor.locale_service import LocaleService

if TYPE_CHECKING:
    from reflex.state import ComputedVar

locale_service = LocaleService.get()
translations = {
    "locale-1": {
        "test_id": "locale-1.test_id",
        "test_dependency_id": "locale-1.test_dependency_id.{0}",
    },
    "locale-2": {
        "test_id": "locale-2.test_id",
        "test_dependency_id": "locale-2.test_dependency_id.{0}",
    },
}
MonkeyPatch().setattr(
    locale_service,
    locale_service.get_text.__name__,
    lambda locale, lid: translations[locale][lid],
)


class TestState(rx.State):
    current_locale: str = "locale-1"
    some_var: int = 1

    @label_var(label_id="test_id")
    def label_string_value(self) -> None:
        pass

    @label_var(label_id="test_dependency_id", deps=["some_var"])
    def label_with_dependencies(self) -> list[int]:
        return [self.some_var]


def test_label_var_inital_state() -> None:
    state = TestState()
    assert state.label_string_value == "locale-1.test_id"
    assert state.label_with_dependencies == "locale-1.test_dependency_id.1"


def test_label_var_locale_change() -> None:
    state = TestState()
    assert state.label_string_value == "locale-1.test_id"
    assert state.label_with_dependencies == "locale-1.test_dependency_id.1"

    state.current_locale = "locale-2"
    assert state.label_string_value == "locale-2.test_id"
    assert state.label_with_dependencies == "locale-2.test_dependency_id.1"


def test_label_var_dependecy_update() -> None:
    state = TestState()
    assert state.label_with_dependencies == "locale-1.test_dependency_id.1"

    state.some_var = 245
    assert state.label_with_dependencies == "locale-1.test_dependency_id.245"

    state.current_locale = "locale-2"
    assert state.label_with_dependencies == "locale-2.test_dependency_id.245"


def test_label_var_metadata_serialisation_stuff() -> None:
    label_string = cast("ComputedVar[str]", TestState.label_string_value)
    assert None in label_string._static_deps
    assert "current_locale" in label_string._static_deps[None]

    label_string_deps = cast("ComputedVar[str]", TestState.label_with_dependencies)
    assert None in label_string_deps._static_deps
    assert "current_locale" in label_string_deps._static_deps[None]
    assert "some_var" in label_string_deps._static_deps[None]
