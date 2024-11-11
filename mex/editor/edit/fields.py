from mex.common.models import MERGED_MODEL_CLASSES_BY_NAME
from mex.common.types import Link, Text
from mex.common.types.temporal_entity import (
    Year,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)
from mex.common.types.vocabulary import (
    AccessRestriction,
    ActivityType,
    AnonymizationPseudonymization,
    APIType,
    BibliographicResourceType,
    ConsentStatus,
    ConsentType,
    DataProcessingState,
    Frequency,
    Language,
    License,
    MIMEType,
    PersonalData,
    ResourceCreationMethod,
    ResourceTypeGeneral,
    TechnicalAccessibility,
    Theme,
)
from mex.common.utils import contains_only_types, group_fields_by_class_name

# TODO(ND): could this be MERGEABLE_FIELDS_BY_CLASS_NAME?
NEVER_EDITABLE_FIELDS = [
    "hadPrimarySource",
    "identifierInPrimarySource",
    "entityType",
]

# TODO(ND): use this from mex backend/common
TEXT_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    MERGED_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, Text),
)
LINK_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    MERGED_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, Link),
)

# new
VOCABULARY_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    MERGED_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(
        field_info,
        AccessRestriction,
        ActivityType,
        AnonymizationPseudonymization,
        APIType,
        BibliographicResourceType,
        ConsentStatus,
        ConsentType,
        DataProcessingState,
        Frequency,
        Language,
        License,
        MIMEType,
        PersonalData,
        ResourceCreationMethod,
        ResourceTypeGeneral,
        TechnicalAccessibility,
        Theme,
    ),
)

TEMPORAL_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    MERGED_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(
        field_info,
        Year,
        YearMonth,
        YearMonthDay,
        YearMonthDayTime,
    ),
)

VOCABULARY_CLASSES_BY_NAME = {
    "AccessRestriction": AccessRestriction,
    "ActivityType": ActivityType,
    "AnonymizationPseudonymization": AnonymizationPseudonymization,
    "APIType": APIType,
    "BibliographicResourceType": BibliographicResourceType,
    "ConsentStatus": ConsentStatus,
    "ConsentType": ConsentType,
    "DataProcessingState": DataProcessingState,
    "Frequency": Frequency,
    "Language": Language,
    "License": License,
    "MIMEType": MIMEType,
    "PersonalData": PersonalData,
    "ResourceCreationMethod": ResourceCreationMethod,
    "ResourceTypeGeneral": ResourceTypeGeneral,
    "TechnicalAccessibility": TechnicalAccessibility,
    "Theme": Theme,
}
