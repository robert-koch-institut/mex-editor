"""Written by Claude (Anthropic).

Resolves a pydantic field's real Python annotation into a small type IR
(`Node`). Deliberately does NOT use `model_json_schema()`: that flattens
things we need to know (a `Literal` discriminator becomes `"type":
"string"`; a `VocabularyEnum` becomes a bare regex; `TemporalEntity`
subclasses -- not `str` subclasses, but scalar-shaped via a custom
pydantic-core schema -- get lost). Reading the annotation directly keeps
all of that.
"""
# mypy: ignore-errors
from __future__ import annotations
import typing
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any, Literal, Union
from pydantic import BaseModel, TypeAdapter
from pydantic.fields import FieldInfo


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

    item: "Node"
    min_length: int | None = None
    max_length: int | None = None


@dataclass(frozen=True)
class UnionNode:
    """A field whose value can be any one of several distinct shapes."""

    members: tuple["Node", ...]


@dataclass(frozen=True)
class ScalarNode:
    """A plain value type (str/int/float/bool), with whatever constraints
    (regex pattern, length, bounds) its own type or field definition adds."""

    py_type: type
    leaf_cls: type
    pattern: str | None = None
    format: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True)
class UnknownNode:
    """Anything this resolver has no specific rule for. Never silently
    treated as something else -- generators should flag it, not guess."""

    description: str


# A resolved field is exactly one of these shapes.
Node = ObjectRef | EnumRef | LiteralNode | ListNode | UnionNode | ScalarNode | UnknownNode


@dataclass(frozen=True)
class ResolvedField:
    """A resolved node plus whether the field also allows `None`."""

    node: Node
    nullable: bool


def _is_union(origin: Any) -> bool:
    # Covers both typing.Union[...] and the `X | Y` (PEP 604) spelling.
    import types as _t

    return origin is Union or (hasattr(_t, "UnionType") and origin is _t.UnionType)


def _flatten(items: tuple[Any, ...]) -> tuple[Any, ...]:
    # Annotated[X, FieldInfo(...)] nests real constraints inside that
    # FieldInfo's own .metadata -- unwrap so callers see plain constraint
    # objects only.
    flat: list[Any] = []
    for item in items:
        flat.extend(_flatten(tuple(item.metadata))) if isinstance(item, FieldInfo) else flat.append(item)
    return tuple(flat)


def _meta_constraints(metadata: tuple[Any, ...]) -> dict[str, Any]:
    # Duck-typed lookup over annotated_types-style constraint objects, so
    # this keeps working for constraint types we've never seen.
    r: dict[str, Any] = {}
    for item in metadata:
        if (v := getattr(item, "min_length", None)) is not None:
            r["min_length"] = v
        if (v := getattr(item, "max_length", None)) is not None:
            r["max_length"] = v
        if (v := getattr(item, "ge", None)) is not None:
            r["minimum"] = v
        elif (v := getattr(item, "gt", None)) is not None:
            r.setdefault("minimum", v)
        if (v := getattr(item, "le", None)) is not None:
            r["maximum"] = v
        elif (v := getattr(item, "lt", None)) is not None:
            r.setdefault("maximum", v)
        if v := getattr(item, "pattern", None):
            r["pattern"] = v
    return r


@lru_cache(maxsize=None)
def _scalar_facts(leaf_cls: type) -> dict[str, Any]:
    # Ask pydantic what JSON type a class serializes to. Generic on
    # purpose: works even for scalar-shaped types that aren't str/int/float
    # subclasses (mex-common's TemporalEntity implements its own
    # pydantic-core schema instead of subclassing str).
    try:
        s = TypeAdapter(leaf_cls).json_schema()
    except Exception:
        return {}
    keys = {"json_type": "type", "pattern": "pattern", "format": "format",
            "min_length": "minLength", "max_length": "maxLength", "minimum": "minimum", "maximum": "maximum"}
    return {k: s.get(v) for k, v in keys.items()}


_JSON_TO_PY = {"string": str, "integer": int, "number": float, "boolean": bool}


def resolve_annotation(annotation: Any, metadata: tuple[Any, ...] = ()) -> ResolvedField:
    """Resolve one field's annotation (+ any `Annotated`/`Field(...)`
    metadata) into a `Node`. Recursive: unwraps `Annotated`, `Optional`/
    `Union`, and `list[...]` before classifying the innermost type."""
    if hasattr(annotation, "__metadata__"):
        return resolve_annotation(annotation.__origin__, (*metadata, *_flatten(annotation.__metadata__)))

    origin = typing.get_origin(annotation)

    if _is_union(origin):
        args = typing.get_args(annotation)
        non_none = [a for a in args if a is not type(None)]
        nullable = len(non_none) != len(args)
        if len(non_none) == 1:  # the common Optional[X] case
            r = resolve_annotation(non_none[0], metadata)
            return ResolvedField(r.node, nullable or r.nullable)
        return ResolvedField(UnionNode(tuple(resolve_annotation(a).node for a in non_none)), nullable)

    if origin is list:
        args = typing.get_args(annotation)
        item = resolve_annotation(args[0]).node if args else UnknownNode("list item")
        c = _meta_constraints(metadata)
        return ResolvedField(ListNode(item, c.get("min_length"), c.get("max_length")), False)

    if origin is Literal:
        return ResolvedField(LiteralNode(typing.get_args(annotation)), False)

    if isinstance(annotation, type):
        if annotation is bool:
            return ResolvedField(ScalarNode(bool, bool), False)
        if issubclass(annotation, Enum):
            return ResolvedField(EnumRef(annotation), False)
        if issubclass(annotation, BaseModel):
            return ResolvedField(ObjectRef(annotation), False)
        facts = _scalar_facts(annotation)
        py_type = _JSON_TO_PY.get(facts.get("json_type"))
        if py_type is not None:
            overlay = _meta_constraints(metadata)
            m = {**facts, **{k: v for k, v in overlay.items() if v is not None}}
            return ResolvedField(
                ScalarNode(py_type, annotation, m.get("pattern"), m.get("format"),
                           m.get("min_length"), m.get("max_length"), m.get("minimum"), m.get("maximum")),
                False,
            )

    return ResolvedField(UnknownNode(repr(annotation)), False)


@dataclass(frozen=True)
class FieldSpec:
    """One resolved field of a model: its Python name, JSON alias
    (`entityType` -> `$type`), resolved node, and whether it's required."""

    py_name: str
    alias: str
    node: Node
    required: bool
    nullable: bool
    description: str | None


def fields_of(model: type[BaseModel]) -> list[FieldSpec]:
    """All declared fields of `model`, resolved via `resolve_annotation`."""
    out = []
    for name, info in model.model_fields.items():
        r = resolve_annotation(info.annotation, tuple(info.metadata))
        out.append(FieldSpec(name, info.alias or name, r.node, info.is_required(), r.nullable, info.description))
    return out
