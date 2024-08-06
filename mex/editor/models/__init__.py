from importlib.resources import files

import yaml
from pydantic import TypeAdapter

from mex.editor.models.config import ModelConfig

__all__ = (
    "ModelConfig",
    "MODEL_CONFIG_BY_STEM_TYPE",
)
MODEL_CONFIG_BY_STEM_TYPE = TypeAdapter(dict[str, ModelConfig]).validate_python(
    yaml.safe_load(files("mex.editor").joinpath("models.yaml").open())
)
