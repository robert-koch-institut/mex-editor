from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from enum import Enum

    from pydantic import BaseModel


@dataclass(frozen=True)
class Bundle:
    """One named group of pydantic models that get generated together.

    The input to `zod_generator.generate_zod_schemas`.

    For example `Bundle("Activity", [ExtractedActivity, MergedActivity, ...])`.
    `name` becomes the output folder/file name (kebab-cased); `models` are the
    "entity types" that get their own generated file.
    """

    name: str
    models: list[type[BaseModel]]


@dataclass(frozen=True)
class ObjectRef:
    """A field whose value is another pydantic model."""

    cls: type[BaseModel]


@dataclass(frozen=True)
class EnumRef:
    """A field whose value is one member of a Python `Enum`."""

    cls: type[Enum]


@dataclass(frozen=True)
class LiteralNode:
    """A field with a fixed set of literal values (e.g. `$type`)."""

    values: tuple[Any, ...]


@dataclass(frozen=True)
class ListNode:
    """A field whose value is a list of some other node."""

    item: Node
    min_length: int | None = None
    max_length: int | None = None


@dataclass(frozen=True)
class UnionNode:
    """A field whose value can be any one of several distinct shapes."""

    members: tuple[Node, ...]


@dataclass(frozen=True)
class ScalarNode:
    """A plain value type (str/int/float/bool), plus its constraints.

    Constraints (regex pattern, length, bounds) come from whatever its own
    type or field definition adds.
    """

    py_type: type
    leaf_cls: type
    pattern: str | None = None
    format: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    # `minimum`/`maximum` are inclusive (pydantic's ge/le), the `exclusive_*`
    # pair is not (gt/lt). Kept apart on purpose: collapsing gt onto minimum
    # would let the browser accept a value the backend rejects.
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None


@dataclass(frozen=True)
class UnknownNode:
    """Anything this resolver has no specific rule for.

    Never silently treated as something else -- generators should flag it,
    not guess.
    """

    description: str


# A resolved field is exactly one of these shapes.
Node = (
    ObjectRef | EnumRef | LiteralNode | ListNode | UnionNode | ScalarNode | UnknownNode
)


@dataclass(frozen=True)
class ResolvedField:
    """A resolved node plus whether the field also allows `None`.

    Produced by `types.resolve_annotation`.
    """

    node: Node
    nullable: bool


@dataclass(frozen=True)
class FieldSpec:
    """One resolved field of a model.

    Carries its Python name, JSON alias (`entityType` -> `$type`), resolved
    node, and whether it's required.
    """

    py_name: str
    alias: str
    node: Node
    required: bool
    nullable: bool


@dataclass(frozen=True)
class ModelDef:
    """A def backed by a pydantic model.

    `extends` is set when this def's fields were factored out of a base shared
    with a sibling model in the same bundle (see `_factor_bases`) -- `fields`
    then excludes whatever the base already covers.
    """

    cls: type[BaseModel]
    fields: list[FieldSpec]
    extends: str | None = None


@dataclass(frozen=True)
class EnumDef:
    """A def backed by a fixed-member `Enum` class."""

    cls: type[Enum]


DefEntry = ModelDef | EnumDef


@dataclass
class SchemaIndex:
    """Everything generators need about the defs collected from the bundles.

    Namely: every def, and which bundle "owns" it (used by exactly one) or
    shares it (used by more than one). Built by
    `collection.build_schema_index`.
    """

    defs: dict[str, DefEntry] = field(default_factory=dict)
    bundles_using_def: dict[str, set[str]] = field(default_factory=dict)

    def shared_defs(self) -> set[str]:
        """Def names referenced by more than one bundle."""
        return {n for n, u in self.bundles_using_def.items() if len(u) > 1}

    def owning_bundle(self, def_name: str) -> str | None:
        """The single bundle that owns `def_name`, or None if it's shared."""
        u = self.bundles_using_def.get(def_name, set())
        return next(iter(u)) if len(u) == 1 else None


@dataclass
class ZodResult:
    """One def's generated Zod code, plus what it needs imported.

    Imports are other defs' schema constants (`def_refs`) and shared pattern
    constants (`pattern_names`).
    """

    code: str = ""
    def_refs: set[str] = field(default_factory=set)
    pattern_names: set[str] = field(default_factory=set)
    # Every node that fell through to z.unknown(). UnknownNode's own docstring
    # says generators must flag rather than guess -- this is that flag.
    unknowns: list[str] = field(default_factory=list)
