from unittest.mock import MagicMock, patch

import pytest

from mex.common.models import AnyExtractedModel
from mex.editor.aux_search.models import AuxResult
from mex.editor.aux_search.state import AuxState
from mex.editor.aux_search.transform import (
    models_to_all_properties,
    transform_models_to_results,
)
from mex.editor.models import EditorValue


@pytest.fixture
def app_state() -> AuxState:
    return AuxState()


def test_models_to_all_properties_no_models():
    result = models_to_all_properties([])
    assert result == []


def test_models_to_all_properties_single_model():
    model = MagicMock(spec=AnyExtractedModel)
    model.attr1 = "value1"
    model.attr2 = "value2"
    model.identifier = "id1"

    with (
        patch(
            "builtins.vars", return_value={"attr1": model.attr1, "attr2": model.attr2}
        ),
        patch(
            "mex.editor.transform.transform_values",
            return_value=[EditorValue(text="transformed_value")],
        ),
    ):
        result = models_to_all_properties([model])

    assert len(result) == 2
    assert result[0].text == "transformed_value"
    assert result[1].text == "transformed_value"


def test_models_to_all_properties_multiple_models():
    model1 = MagicMock(spec=AnyExtractedModel)
    model1.attr1 = "value1"
    model1.attr2 = "value2"
    model1.identifier = "id1"

    model2 = MagicMock(spec=AnyExtractedModel)
    model2.attr1 = "value3"
    model2.attr2 = "value4"
    model2.identifier = "id2"

    with patch(
        "mex.editor.transform.transform_values",
        return_value=[EditorValue(text="transformed_value")],
    ):
        result = models_to_all_properties([model1, model2])

    assert len(result) == 4
    assert all(r.text == "transformed_value" for r in result)


def test_models_to_all_properties_no_attributes():
    model = MagicMock(spec=AnyExtractedModel)
    model.identifier = "id1"

    with patch(
        "mex.editor.transform.transform_values",
        return_value=[EditorValue(text="transformed_value")],
    ):
        result = models_to_all_properties([model])

    assert len(result) == 1
    assert result[0].text == "transformed_value"


def test_transform_models_to_results_single_model():
    model = MagicMock(spec=AnyExtractedModel)
    model.identifier = "id1"

    with (
        patch("mex.editor.transform.transform_models_to_title", return_value="title"),
        patch(
            "mex.editor.transform.transform_models_to_preview", return_value="preview"
        ),
        patch(
            "mex.editor.aux_search.transform.models_to_all_properties",
            return_value=[EditorValue(text="property")],
        ),
    ):
        result = transform_models_to_results([model])

    assert len(result) == 1
    assert isinstance(result[0], AuxResult)
    assert result[0].identifier == "id1"
    assert result[0].title == "title"
    assert result[0].preview == "preview"
    assert len(result[0].all_properties) == 1
    assert result[0].all_properties[0].text == "property"


def test_transform_models_to_results_multiple_models():
    model1 = MagicMock(spec=AnyExtractedModel)
    model1.identifier = "id1"

    model2 = MagicMock(spec=AnyExtractedModel)
    model2.identifier = "id2"

    with (
        patch("mex.editor.transform.transform_models_to_title", return_value="title"),
        patch(
            "mex.editor.transform.transform_models_to_preview", return_value="preview"
        ),
        patch(
            "mex.editor.aux_search.transform.models_to_all_properties",
            return_value=[EditorValue(text="property")],
        ),
    ):
        result = transform_models_to_results([model1, model2])

    assert len(result) == 2
    assert result[0].identifier == "id1"
    assert result[0].title == "title"
    assert result[0].preview == "preview"
    assert len(result[0].all_properties) == 1
    assert result[0].all_properties[0].text == "property"
    assert result[1].identifier == "id2"
    assert result[1].title == "title"
    assert result[1].preview == "preview"
    assert len(result[1].all_properties) == 1
    assert result[1].all_properties[0].text == "property"
