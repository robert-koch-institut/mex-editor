from importlib.resources import files

import yaml
from pydantic import TypeAdapter

from mex.editor.types import ModelConfig

DEFAULT_MODEL_CONFIG_PATH = files("mex.editor").joinpath("models.yaml")
MODEL_CONFIG_BY_STEM_TYPE = TypeAdapter(dict[str, ModelConfig]).validate_python(
    yaml.safe_load(DEFAULT_MODEL_CONFIG_PATH.open())
)
