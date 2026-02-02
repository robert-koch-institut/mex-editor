from typing import cast

from mex.common.fields import (
    ALL_MODEL_CLASSES_BY_NAME,
    ALL_TYPES_BY_FIELDS_BY_CLASS_NAMES,
    REFERENCE_FIELDS_BY_CLASS_NAME,
    TEMPORAL_FIELDS_BY_CLASS_NAME,
)
from mex.common.types import (
    MERGED_IDENTIFIER_CLASSES,
    AnyTemporalEntity,
    TemporalEntityPrecision,
)
from mex.common.utils import contains_any_types, get_all_fields

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
            key=lambda precision: list(TemporalEntityPrecision).index(precision),
        )
        for field_name in field_names
    }
    for class_name, field_names in TEMPORAL_FIELDS_BY_CLASS_NAME.items()
}

# TODO(FE): Same as https://github.com/robert-koch-institut/mex-backend/blob/main/mex/backend/fields.py#L61
# needs to be moved to common.

# allowed entity types grouped for reference fields
REFERENCED_ENTITY_TYPES_BY_FIELD_BY_CLASS_NAME = {
    class_name: {
        field_name: sorted(
            identifier_class.__name__.removesuffix("Identifier")
            for identifier_class in MERGED_IDENTIFIER_CLASSES
            if contains_any_types(
                get_all_fields(ALL_MODEL_CLASSES_BY_NAME[class_name])[field_name],
                identifier_class,
            )
        )
        for field_name in field_names
    }
    for class_name, field_names in REFERENCE_FIELDS_BY_CLASS_NAME.items()
}

# stringified allowed types grouped by field and class names
STRINGIFIED_TYPES_BY_FIELD_BY_CLASS_NAME = {
    class_name: {
        field_name: REFERENCED_ENTITY_TYPES_BY_FIELD_BY_CLASS_NAME[class_name].get(
            field_name, sorted(str(field_type.__name__) for field_type in field_types)
        )
        for field_name, field_types in fields.items()
    }
    for class_name, fields in ALL_TYPES_BY_FIELDS_BY_CLASS_NAMES.items()
}
