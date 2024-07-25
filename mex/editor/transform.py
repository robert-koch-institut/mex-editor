from mex.common.models import AnyExtractedModel, AnyMergedModel
from mex.common.types import Text
from mex.editor.models import MODEL_CONFIG_BY_STEM_TYPE


def render_any_value(value: object) -> str:
    """Simple rendering function to stringify objects."""
    if isinstance(value, dict):
        return ", ".join(f"{k}: {render_any_value(v)}" for k, v in value.items() if v)
    if isinstance(value, list):
        return ", ".join(render_any_value(v) for v in value)
    if isinstance(value, Text):
        return value.value
    if value := str(value).strip():
        return value
    return ""


def render_model_title(model: AnyExtractedModel | AnyMergedModel) -> str:
    """Return a rendered model title."""
    config = MODEL_CONFIG_BY_STEM_TYPE[model.stemType]
    if rendered := render_any_value(getattr(model, config.title)):
        return rendered
    return str(model.entityType)


def render_model_preview(
    model: AnyExtractedModel | AnyMergedModel, sep: str = " \u2010 "
) -> str:
    """Return a rendered model preview separated by given string."""
    config = MODEL_CONFIG_BY_STEM_TYPE[model.stemType]
    fields = model.model_dump(include={*config.preview})
    if rendered := sep.join(
        render_any_value(v) for p in config.preview if (v := fields[p])
    ):
        return rendered
    return str(model.identifier)
