from mex.common.models import AnyExtractedModel
from mex.editor.transform import transform_models_to_preview, transform_models_to_title


def test_render_model_title(dummy_data: list[AnyExtractedModel]) -> None:
    dummy_titles = [transform_models_to_title([d]) for d in dummy_data]
    assert dummy_titles == [
        "ExtractedPrimarySource",
        "ExtractedPrimarySource",
        "info@contact-point.one",
        "help@contact-point.two",
        "OU1",
        "Aktivität 1",
    ]


def test_render_model_preview(dummy_data: list[AnyExtractedModel]) -> None:
    dummy_previews = [transform_models_to_preview([d]) for d in dummy_data]
    assert dummy_previews == [
        "sMgFvmdtJyegb9vkebq04",
        "d0MGZryflsy7PbsBF3ZGXO",
        "gs6yL8KJoXRos9l2ydYFfx",
        "vQHKlAQWWraW9NPoB5Ewq",
        "gIyDlXYbq0JwItPRU0NcFN",
        "value: A1 \u2010 cWWm02l1c6cucKjIhkFqY4 \u2010 1999-12-24 \u2010 2023-01-01",
    ]
