import re
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from pydantic_core.core_schema import PlainValidatorFunctionSchema

# ---------------------------------------------------------------------------
# TemporalEntity-style scalar types: not str subclasses, but scalar-shaped
# via a custom pydantic-core schema -- exactly the case types.py's
# docstring calls out `model_json_schema()` as losing track of.
# ---------------------------------------------------------------------------


class _PatternedString:  # noqa: PLW1641
    """A scalar-shaped type that validates against a regex.

    Not a `str` subclass: it carries its own pydantic-core schema, exactly like
    mex-common's `TemporalEntity` family.
    """

    _pattern: str

    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.value == other.value

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: Any,  # noqa: ANN401
    ) -> PlainValidatorFunctionSchema:
        """Validate from a string, serialise back to one."""
        from pydantic_core import core_schema  # noqa: PLC0415

        def validate(value: object) -> _PatternedString:
            if isinstance(value, cls):
                return value
            if not isinstance(value, str) or not re.fullmatch(cls._pattern, value):
                msg = f"Invalid {cls.__name__}: {value!r}"
                raise ValueError(msg)
            return cls(value)

        return core_schema.no_info_plain_validator_function(
            validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: v.value
            ),
            json_schema_input_schema=core_schema.str_schema(pattern=cls._pattern),
        )


# Stand-ins for mex-common's `TemporalEntity` family: scalar-shaped via a
# custom core schema, NOT `str` subclasses. A union of these exercises
# UnionNode-of-patterned-scalars (see `ExtractedPerson.birth_date`).
class Year(_PatternedString):
    _pattern = r"^\d{4}$"


class YearMonth(_PatternedString):
    _pattern = r"^\d{4}-\d{2}$"


class YearMonthDay(_PatternedString):
    _pattern = r"^\d{4}-\d{2}-\d{2}$"


# ---------------------------------------------------------------------------
# Plain domain types
# ---------------------------------------------------------------------------

# Synthetic on purpose: these models stand in for mex-common without
# importing it, so this is deliberately its own literal, not
# `mex.common.types.IDENTIFIER_PATTERN`.
IDENTIFIER_PATTERN = r"^[a-zA-Z0-9]{14,22}$"


# Used by both bundles below, so it gets factored into shared.ts (EnumRef).
class Status(str, Enum):  # noqa: UP042
    ACTIVE = "active"
    INACTIVE = "inactive"


class Address(BaseModel):
    street: str
    zip_code: str = Field(alias="zipCode", pattern=r"^\d{5}$")

    model_config = {"populate_by_name": True}


# Shared by ExtractedOrganization and MergedOrganization, so it is factored
# out into its own def and both extend it.
class OrganizationBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    identifier: str = Field(pattern=IDENTIFIER_PATTERN)


# The kitchen sink: ScalarNode with pattern/length/bounds, EnumRef, ObjectRef,
# ListNode with bounds, single- and multi-value LiteralNode, exclusive vs
# inclusive numeric bounds, and nullable-not-required (.nullish()).
class ExtractedOrganization(OrganizationBase):
    entity_type: Literal["ExtractedOrganization"] = Field(
        alias="entityType", default="ExtractedOrganization"
    )
    email: str = Field(
        pattern="^[^@ \\t\\r\\n]+@[^@ \\t\\r\\n]+\\.[^@ \\t\\r\\n]+$",
        json_schema_extra={"format": "email"},
    )
    employee_count: int = Field(alias="employeeCount", ge=0, le=100_000)
    tags: list[str] = Field(min_length=1, max_length=5)
    status: Status
    address: Address
    website: str | None = None  # nullable, NOT required -> .nullish()
    # Exclusive bounds: must stay exclusive all the way into Zod, not be
    # widened to the inclusive .min()/.max().
    rating: float | None = Field(default=None, gt=0, lt=5)
    # Multi-value Literal: a single `z.literal(...)` per value would not be
    # valid TypeScript.
    tier: Literal["gold", "silver"] | None = None
    # A nullable single-value literal: must keep its .nullish(), which the
    # old "any single-value literal needs no wrapper" rule threw away.
    scope: Literal["public"] | None = None

    model_config = {"populate_by_name": True}


class MergedOrganization(OrganizationBase):
    entity_type: Literal["MergedOrganization"] = Field(
        alias="entityType", default="MergedOrganization"
    )
    status: Status
    address: Address | None = None

    model_config = {"populate_by_name": True}


class PersonBase(BaseModel):
    given_name: str = Field(alias="givenName")
    family_name: str = Field(alias="familyName")

    model_config = {"populate_by_name": True}


# Covers nullable-AND-required (.nullable(), not .nullish()) via `birth_date`,
# plus a union of three patterned scalar types.
class ExtractedPerson(PersonBase):
    entity_type: Literal["ExtractedPerson"] = Field(
        alias="entityType", default="ExtractedPerson"
    )
    identifier: str = Field(pattern=IDENTIFIER_PATTERN)
    status: Status
    birth_date: YearMonthDay | YearMonth | Year | None = Field(
        alias="birthDate"
    )  # nullable, REQUIRED -> .nullable()

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}


class MergedPerson(PersonBase):
    entity_type: Literal["MergedPerson"] = Field(
        alias="entityType", default="MergedPerson"
    )
    identifier: str = Field(pattern=IDENTIFIER_PATTERN)
    status: Status

    model_config = {"populate_by_name": True}


class Opaque:
    """A type pydantic cannot describe as JSON at all."""


class HasOpaqueField(BaseModel):
    name: str
    thing: Opaque

    model_config = {"arbitrary_types_allowed": True}


class UnionWithFieldConstraint(BaseModel):
    code: YearMonthDay | Year = Field(min_length=4)

    model_config = {"arbitrary_types_allowed": True}
