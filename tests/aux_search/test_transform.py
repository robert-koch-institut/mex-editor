from unittest.mock import MagicMock, Mock, patch

from mex.common.models import AnyExtractedModel
from mex.editor.aux_search.models import AuxResult
from mex.editor.aux_search.transform import (
    model_to_all_properties,
    transform_models_to_results,
)
from mex.editor.models import EditorValue


def test_model_to_all_properties() -> None:
    model = MagicMock(spec=AnyExtractedModel)
    model.field1 = "value1"
    model.field2 = "value2"
    model.model_fields = {"field1": Mock(), "field2": Mock()}

    with patch(
        "mex.editor.transform.transform_values",
        side_effect=lambda x, allow_link: [EditorValue(text=f"value{x}")],
    ):
        result = model_to_all_properties(model)

    assert len(result) == 2
    assert result[0].text == "value1"
    assert result[1].text == "value2"


def test_transform_models_to_results_single_model() -> None:
    model = MagicMock(spec=AnyExtractedModel)
    model.identifier = "id1"
    model.stemType = "Organization"
    model.officialName = "name"
    model.shortName = "shortName"
    model.alternativeName = "alternativeName"
    model.wikidataId = "wikidataId"

    with patch(
        "mex.editor.aux_search.transform.model_to_all_properties",
        return_value=[EditorValue(text="property")],
    ):
        result = transform_models_to_results([model])

    assert len(result) == 1
    assert isinstance(result[0], AuxResult)
    assert result[0].identifier == "id1"
    assert result[0].title == [
        EditorValue(
            text="name",
            display_text="name",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        )
    ]
    assert result[0].preview == [
        EditorValue(
            text="shortName",
            display_text="shortName",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        ),
        EditorValue(
            text="alternativeName",
            display_text="alternativeName",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        ),
        EditorValue(
            text="wikidataId",
            display_text="wikidataId",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        ),
    ]
    assert len(result[0].all_properties) == 1
    assert result[0].all_properties[0].text == "property"
    assert result[0].show_properties is False


def test_transform_models_to_results_multiple_models() -> None:
    model1 = MagicMock(spec=AnyExtractedModel)
    model1.identifier = "id1"
    model1.stemType = "Organization"
    model1.officialName = "name1"
    model1.shortName = "shortName1"
    model1.alternativeName = "alternativeName1"
    model1.wikidataId = "wikidataId1"

    model2 = MagicMock(spec=AnyExtractedModel)
    model2.identifier = "id2"
    model2.stemType = "Organization"
    model2.officialName = "name2"
    model2.shortName = "shortName2"
    model2.alternativeName = "alternativeName2"
    model2.wikidataId = "wikidataId2"

    with patch(
        "mex.editor.aux_search.transform.model_to_all_properties",
        return_value=[EditorValue(text="property")],
    ):
        result = transform_models_to_results([model1, model2])

    assert len(result) == 2
    assert result[0].identifier == "id1"
    assert result[0].title == [
        EditorValue(
            text="name1",
            display_text="name1",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        )
    ]
    assert result[0].preview == [
        EditorValue(
            text="shortName1",
            display_text="shortName1",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        ),
        EditorValue(
            text="alternativeName1",
            display_text="alternativeName1",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        ),
        EditorValue(
            text="wikidataId1",
            display_text="wikidataId1",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        ),
    ]
    assert len(result[0].all_properties) == 1
    assert result[0].all_properties[0].text == "property"

    assert result[1].identifier == "id2"
    assert result[1].title == [
        EditorValue(
            text="name2",
            display_text="name2",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        )
    ]
    assert result[1].preview == [
        EditorValue(
            text="shortName2",
            display_text="shortName2",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        ),
        EditorValue(
            text="alternativeName2",
            display_text="alternativeName2",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        ),
        EditorValue(
            text="wikidataId2",
            display_text="wikidataId2",
            badge=None,
            href=None,
            external=False,
            enabled=True,
            resolved=True,
        ),
    ]
    assert len(result[1].all_properties) == 1
    assert result[1].all_properties[0].text == "property"
