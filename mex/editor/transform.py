import functools

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger
from mex.common.models import AnyExtractedModel, AnyMergedModel
from mex.common.types import Identifier, Link, Text
from mex.editor.models import MODEL_CONFIG_BY_STEM_TYPE


def render_any_value(value: object, sep: str = ", ") -> str:
    """Simple rendering function to stringify objects."""
    if isinstance(value, list):
        return sep.join(render_any_value(v) for v in value)
    if isinstance(value, Text):
        return value.value
    if isinstance(value, Link):
        return value.title or value.url
    if isinstance(value, Identifier):
        return get_title_for_merged_id(value)
    if value and (value := str(value).strip()):
        return value
    return ""


def render_model_title(model: AnyExtractedModel | AnyMergedModel) -> str:
    """Return a rendered model title."""
    config = MODEL_CONFIG_BY_STEM_TYPE[model.stemType]
    if rendered := render_any_value(getattr(model, config.title)):
        return rendered
    return str(model.identifier)


def render_model_preview(
    model: AnyExtractedModel | AnyMergedModel,
    sep: str = " \u2010 ",
) -> str:
    """Return a rendered model preview separated by given string."""
    config = MODEL_CONFIG_BY_STEM_TYPE[model.stemType]
    if rendered := sep.join(
        value
        for field in config.preview
        if (value := render_any_value(getattr(model, field)))
    ):
        return rendered
    return str(model.entityType)


@functools.lru_cache(maxsize=500)
def get_title_for_merged_id(merged_id: Identifier) -> str:
    """Get a cached preview title for a given merged identifier."""
    try:
        connector = BackendApiConnector.get()
        # item = connector.get_merged_item(merged_id)
        # title = render_model_title(item)
        title = repr((connector, merged_id))
        logger.info(f"resolved {merged_id} to {title[:30]}")
    except Exception as err:
        logger.error("failed resolving %s: %s", merged_id, err)
        title = render_any_value(merged_id)
    return title
