import pytest
from reflex.state import serialize_mutable_proxy

from mex.common.models import ContactPointRuleSetResponse, ExtractedContactPoint
from mex.editor.edit.models import EditorPrimarySource, InputConfig
from mex.editor.edit.state import EditState
from mex.editor.edit.transform import transform_models_to_fields
from mex.editor.models import EditorValue


def test_state_get_primary_sources_by_field_name() -> None:
    state = EditState()
    rule_set = ContactPointRuleSetResponse(stableTargetId="someContactPoint")
    extracted_item = ExtractedContactPoint(
        email="test@foo.bar",
        identifierInPrimarySource="fooBarContactPoint",
        hadPrimarySource="somePrimarySource",
    )
    state.fields = transform_models_to_fields(
        [extracted_item],
        additive=rule_set.additive,
        subtractive=rule_set.subtractive,
        preventive=rule_set.preventive,
    )

    with pytest.raises(ValueError, match="field not found: someField"):
        state._get_primary_sources_by_field_name("someField")

    primary_sources = serialize_mutable_proxy(
        state._get_primary_sources_by_field_name("email")
    )

    assert primary_sources == [
        EditorPrimarySource(
            name=EditorValue(text="somePrimarySource", href="/item/somePrimarySource"),
            identifier="somePrimarySource",
            input_config=InputConfig(),
            editor_values=[EditorValue(text="test@foo.bar")],
        ),
        EditorPrimarySource(
            name=EditorValue(text="00000000000000", href="/item/00000000000000"),
            identifier="00000000000000",
            input_config=InputConfig(editable_text=True),
            editor_values=[],
        ),
    ]
