import pytest

from mex.common.models import (
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    AdditiveContactPoint,
    AnyExtractedModel,
    AnyMergedModel,
    AnyRuleModel,
    ExtractedContactPoint,
    MergedContactPoint,
)
from mex.common.types import MergedContactPointIdentifier, MergedPrimarySourceIdentifier
from mex.editor.edit.transform import _get_primary_source_id_from_model


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (
            ExtractedContactPoint(
                email="info@rki.de",
                hadPrimarySource=MergedPrimarySourceIdentifier(
                    "gGdOIbDIHRt35He616Fv5q"
                ),
                identifierInPrimarySource="info",
            ),
            MergedPrimarySourceIdentifier("gGdOIbDIHRt35He616Fv5q"),
        ),
        (
            MergedContactPoint(
                identifier=MergedContactPointIdentifier("t35He616Fv5qxGdOIbDiHR"),
                email="info@rki.de",
            ),
            MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        ),
        (
            AdditiveContactPoint(
                email="example@rki.de",
            ),
            MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
        ),
    ],
)
def test_get_primary_source_id_from_model(
    model: AnyExtractedModel | AnyMergedModel | AnyRuleModel,
    expected: MergedPrimarySourceIdentifier,
) -> None:
    primary_source_id = _get_primary_source_id_from_model(model)
    assert primary_source_id == expected


def test_transform_model_values_to_editor_values() -> None:
    pass


def test_transform_model_to_field() -> None:
    pass


def test_transform_models_to_fields() -> None:
    pass


def test_transform_field_to_preventive() -> None:
    pass


def test_transform_render_value_to_model_type() -> None:
    pass


def test_transform_field_to_subtractive() -> None:
    pass


def test_transform_fields_to_rule_set() -> None:
    pass
