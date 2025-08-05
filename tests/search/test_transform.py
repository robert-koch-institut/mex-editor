from mex.common.models import PreviewOrganizationalUnit
from mex.common.types import Text, TextLanguage
from mex.editor.models import LANGUAGE_VALUE_NONE
from mex.editor.search.transform import transform_models_to_results


def test_transform_models_to_results() -> None:
    # test with empty list
    assert transform_models_to_results([]) == []

    # test with preview unit
    unit_preview = PreviewOrganizationalUnit(
        name=[Text(value="Unit 1", language=TextLanguage.EN)],
        shortName=["OU1"],
        identifier="000000000012345",
    )
    search_result = transform_models_to_results([unit_preview])
    assert len(search_result) == 1
    assert search_result[0].dict() == {
        "identifier": "000000000012345",
        "stem_type": "OrganizationalUnit",
        "title": [
            {
                "text": "OU1",
                "badge": LANGUAGE_VALUE_NONE,
                "being_edited": False,
                "href": None,
                "identifier": None,
                "external": False,
                "enabled": True,
            }
        ],
        "preview": [
            {
                "text": "Unit 1",
                "badge": "EN",
                "being_edited": False,
                "href": None,
                "identifier": None,
                "external": False,
                "enabled": True,
            }
        ],
    }
