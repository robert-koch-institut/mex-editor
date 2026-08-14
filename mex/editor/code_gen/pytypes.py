"""Resolves pydantic field annotations into a small type IR -- from the
real Python types, not model_json_schema()."""
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
    cls: type[BaseModel]


@dataclass(frozen=True)
class EnumRef:
    cls: type[Enum]


@dataclass(frozen=True)
class LiteralNode:
    values: tuple[Any, ...]


@dataclass(frozen=True)
class ListNode:
    item: "Node"
    min_length: int | None = None
    max_length: int | None = None


@dataclass(frozen=True)
class UnionNode:
    members: tuple["Node", ...]


@dataclass(frozen=True)
class ScalarNode:
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
    description: str


Node = ObjectRef | EnumRef | LiteralNode | ListNode | UnionNode | ScalarNode | UnknownNode


@dataclass(frozen=True)
class ResolvedField:
    node: Node
    nullable: bool


def _is_union(origin: Any) -> bool:
    import types as _t
    return origin is Union or (hasattr(_t, "UnionType") and origin is _t.UnionType)


def _flatten(items: tuple[Any, ...]) -> tuple[Any, ...]:
    flat: list[Any] = []
    for item in items:
        flat.extend(_flatten(tuple(item.metadata))) if isinstance(item, FieldInfo) else flat.append(item)
    return tuple(flat)


def _meta_constraints(metadata: tuple[Any, ...]) -> dict[str, Any]:
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
    """Ask pydantic what JSON type a class serializes to -- generic, works
    even for non-str-subclass scalar-shaped types (e.g. mex-common's
    TemporalEntity)."""
    try:
        s = TypeAdapter(leaf_cls).json_schema()
    except Exception:
        return {}
    return {k: s.get(v) for k, v in {
        "json_type": "type", "pattern": "pattern", "format": "format",
        "min_length": "minLength", "max_length": "maxLength",
        "minimum": "minimum", "maximum": "maximum",
    }.items()}


_JSON_TO_PY = {"string": str, "integer": int, "number": float, "boolean": bool}


def resolve_annotation(annotation: Any, metadata: tuple[Any, ...] = ()) -> ResolvedField:
    if hasattr(annotation, "__metadata__"):
        return resolve_annotation(annotation.__origin__, (*metadata, *_flatten(annotation.__metadata__)))

    origin = typing.get_origin(annotation)

    if _is_union(origin):
        args = typing.get_args(annotation)
        non_none = [a for a in args if a is not type(None)]
        nullable = len(non_none) != len(args)
        if len(non_none) == 1:
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
    py_name: str
    alias: str
    node: Node
    required: bool
    nullable: bool
    description: str | None


def fields_of(model: type[BaseModel]) -> list[FieldSpec]:
    out = []
    for name, info in model.model_fields.items():
        r = resolve_annotation(info.annotation, tuple(info.metadata))
        out.append(FieldSpec(name, info.alias or name, r.node, info.is_required(), r.nullable, info.description))
    return out
