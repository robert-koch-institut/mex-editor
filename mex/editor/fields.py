from mex.common.fields import ALL_MODEL_CLASSES_BY_NAME

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
