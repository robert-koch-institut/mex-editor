from typing import TYPE_CHECKING, cast

from mex.common.fields import (
    ALL_MODEL_CLASSES_BY_NAME,
    ALL_TYPES_BY_FIELDS_BY_CLASS_NAMES,
    TEMPORAL_FIELDS_BY_CLASS_NAME,
)

if TYPE_CHECKING:
    from mex.common.types import AnyTemporalEntity

# TODO(ND): move these lookups to mex.common.fields

# list of fields by class name that are not allowed to be null or an empty list
REQUIRED_FIELDS_BY_CLASS_NAME = {
    name: sorted(
        {
            field_name
            for field_name, field_info in cls.model_fields.items()
            if field_info.is_required()
        }
    )
    for name, cls in ALL_MODEL_CLASSES_BY_NAME.items()
}


# allowed temporal precisions grouped by field and class names
TEMPORAL_PRECISIONS_BY_FIELD_BY_CLASS_NAMES = {
    class_name: {
        field_name: sorted(
            {
                precision
                for temporal_type in ALL_TYPES_BY_FIELDS_BY_CLASS_NAMES[class_name][
                    field_name
                ]
                for precision in cast(
                    "type[AnyTemporalEntity]", temporal_type
                ).ALLOWED_PRECISION_LEVELS
            },
            key=lambda precision: precision.value,
        )
        for field_name in field_names
    }
    for class_name, field_names in TEMPORAL_FIELDS_BY_CLASS_NAME.items()
}
