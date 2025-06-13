from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
from mex.common.models.resource import (
    AdditiveResource,
    PreventiveResource,
    SubtractiveResource,
)
from mex.common.types.identifier import MergedPrimarySourceIdentifier
from mex.editor.create.transform import transform_model_to_template_fields


def test_transform_model_to_template_fields() -> None:
    editor_fields = transform_model_to_template_fields(
        entity_type="ExtractedResource",
        additive=AdditiveResource(),
        subtractive=SubtractiveResource(),
        preventive=PreventiveResource(),
    )

    assert len(editor_fields) == len(
        MERGEABLE_FIELDS_BY_CLASS_NAME["ExtractedResource"]
    )
    fields_by_name = {f.name: f for f in editor_fields}
    assert fields_by_name["conformsTo"].dict() == {
        "name": "conformsTo",
        "primary_sources": [
            {
                "editor_values": [],
                "enabled": True,
                "identifier": MergedPrimarySourceIdentifier("00000000000000"),
                "input_config": {
                    "allow_additive": True,
                    "badge_default": None,
                    "badge_options": [],
                    "badge_titles": [],
                    "editable_badge": False,
                    "editable_href": False,
                    "editable_identifier": False,
                    "editable_text": True,
                },
                "name": {
                    "badge": None,
                    "being_edited": False,
                    "enabled": True,
                    "external": False,
                    "href": "/item/00000000000000",
                    "identifier": "00000000000000",
                    "text": None,
                },
            },
        ],
    }
    assert fields_by_name["loincId"].dict() == {
        "name": "loincId",
        "primary_sources": [
            {
                "editor_values": [],
                "enabled": True,
                "identifier": MergedPrimarySourceIdentifier("00000000000000"),
                "input_config": {
                    "allow_additive": True,
                    "badge_default": None,
                    "badge_options": [],
                    "badge_titles": [],
                    "editable_badge": False,
                    "editable_href": False,
                    "editable_identifier": False,
                    "editable_text": True,
                },
                "name": {
                    "badge": None,
                    "being_edited": False,
                    "enabled": True,
                    "external": False,
                    "href": "/item/00000000000000",
                    "identifier": "00000000000000",
                    "text": None,
                },
            },
        ],
    }
