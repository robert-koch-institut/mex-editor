import typing
from enum import Enum
from types import UnionType
from typing import Any, Literal, Union

from pydantic import BaseModel, TypeAdapter
from pydantic.fields import FieldInfo

from mex.editor.code_gen.models import (
    EnumRef,
    FieldSpec,
    ListNode,
    LiteralNode,
    ObjectRef,
    ResolvedField,
    ScalarNode,
    UnionNode,
    UnknownNode,
)


def _is_union(origin: object) -> bool:
    """Check whether `origin` is a union, in either spelling.

    Covers both `typing.Union[...]` and `X | Y` (PEP 604).
    """
    return origin is Union or origin is UnionType


def _flatten(items: tuple[Any, ...]) -> tuple[Any, ...]:
    """Unwrap nested `FieldInfo` metadata into plain constraint objects.

    `Annotated[X, FieldInfo(...)]` hides the real constraints inside that
    `FieldInfo`'s own `.metadata`, so callers would otherwise miss them.
    """
    flat: list[Any] = []
    for item in items:
        if isinstance(item, FieldInfo):
            flat.extend(_flatten(tuple(item.metadata)))
        else:
            flat.append(item)
    return tuple(flat)


def _meta_constraints(metadata: tuple[Any, ...]) -> dict[str, Any]:
    """Read whatever constraints an `Annotated`/`Field(...)` chain declares.

    Duck-typed over annotated_types-style objects, so it keeps working for
    constraint types this module has never seen.
    """
    r: dict[str, Any] = {}
    for item in metadata:
        if (v := getattr(item, "min_length", None)) is not None:
            r["min_length"] = v
        if (v := getattr(item, "max_length", None)) is not None:
            r["max_length"] = v
        if (v := getattr(item, "ge", None)) is not None:
            r["minimum"] = v
        if (v := getattr(item, "gt", None)) is not None:
            r["exclusive_minimum"] = v
        if (v := getattr(item, "le", None)) is not None:
            r["maximum"] = v
        if (v := getattr(item, "lt", None)) is not None:
            r["exclusive_maximum"] = v
        if v := getattr(item, "pattern", None):
            r["pattern"] = v
    return r


_SCALAR_FACTS: dict[type, dict[str, Any]] = {}


def _scalar_facts(leaf_cls: type) -> dict[str, Any]:
    """Ask pydantic which JSON type and constraints `leaf_cls` serializes to.

    Generic on purpose: works even for scalar-shaped types that are not
    str/int/float subclasses -- mex-common's `TemporalEntity` implements its
    own pydantic-core schema instead of subclassing `str`.
    """
    if (cached := _SCALAR_FACTS.get(leaf_cls)) is not None:
        return cached
    try:
        s = TypeAdapter(leaf_cls).json_schema()
    except Exception as error:  # noqa: BLE001 -- any failure just means "not a scalar"
        # Keep the reason: it ends up in the UnknownNode description, so a
        # field that silently became z.unknown() can be traced back here.
        reason = f"{type(error).__name__}: {error}"
        return _SCALAR_FACTS.setdefault(leaf_cls, {"error": reason})
    keys = {
        "json_type": "type",
        "pattern": "pattern",
        "format": "format",
        "min_length": "minLength",
        "max_length": "maxLength",
        "minimum": "minimum",
        "maximum": "maximum",
        "exclusive_minimum": "exclusiveMinimum",
        "exclusive_maximum": "exclusiveMaximum",
    }
    facts = {k: s.get(v) for k, v in keys.items()}
    return _SCALAR_FACTS.setdefault(leaf_cls, facts)


_JSON_TO_PY = {"string": str, "integer": int, "number": float, "boolean": bool}


def _resolve_union(annotation: Any, metadata: tuple[Any, ...]) -> ResolvedField:  # noqa: ANN401
    """Resolve a union annotation into a node.

    `Optional[X]` collapses onto X's own node; anything wider stays a union.
    """
    args = typing.get_args(annotation)
    non_none = [a for a in args if a is not type(None)]
    nullable = len(non_none) != len(args)
    if len(non_none) == 1:  # the common Optional[X] case
        r = resolve_annotation(non_none[0], metadata)
        return ResolvedField(r.node, nullable=nullable or r.nullable)
    # Pass `metadata` down: a constraint declared on the field applies to
    # whichever member ends up matching, so dropping it here would silently
    # widen every multi-member union.
    members = tuple(resolve_annotation(a, metadata).node for a in non_none)
    return ResolvedField(UnionNode(members), nullable=nullable)


def _resolve_class(annotation: type, metadata: tuple[Any, ...]) -> ResolvedField:
    """Resolve a bare class annotation into a node.

    Falls back to `UnknownNode` carrying the reason, never a bare guess. `bool`
    needs no special case: pydantic reports it as JSON "boolean", which
    `_JSON_TO_PY` maps straight back.
    """
    if issubclass(annotation, Enum):
        return ResolvedField(EnumRef(annotation), nullable=False)
    if issubclass(annotation, BaseModel):
        return ResolvedField(ObjectRef(annotation), nullable=False)
    facts = _scalar_facts(annotation)
    json_type = facts.get("json_type")
    py_type = _JSON_TO_PY.get(json_type) if isinstance(json_type, str) else None
    if py_type is None:
        reason = facts.get("error") or f"pydantic reports JSON type {json_type!r}"
        return ResolvedField(
            UnknownNode(f"{annotation.__name__} ({reason})"), nullable=False
        )
    overlay = _meta_constraints(metadata)
    m = {**facts, **{k: v for k, v in overlay.items() if v is not None}}
    return ResolvedField(
        ScalarNode(
            py_type=py_type,
            leaf_cls=annotation,
            pattern=m.get("pattern"),
            format=m.get("format"),
            min_length=m.get("min_length"),
            max_length=m.get("max_length"),
            minimum=m.get("minimum"),
            maximum=m.get("maximum"),
            exclusive_minimum=m.get("exclusive_minimum"),
            exclusive_maximum=m.get("exclusive_maximum"),
        ),
        nullable=False,
    )


def resolve_annotation(
    annotation: Any,  # noqa: ANN401 -- takes any type expression a field can carry
    metadata: tuple[Any, ...] = (),
) -> ResolvedField:
    """Resolve one field's annotation into a `Node`.

    Takes any `Annotated`/`Field(...)` metadata into account. Recursive: unwraps
    `Annotated`, `Optional`/`Union`, and `list[...]` before classifying the
    innermost type.

    Reads the annotation directly rather than going through
    `model_json_schema()`, which flattens away things the generator needs: a
    `Literal` discriminator collapses to `"type": "string"`, a `VocabularyEnum`
    to a bare regex, and `TemporalEntity` subclasses -- scalar-shaped via a
    custom pydantic-core schema rather than by subclassing `str` -- vanish
    entirely.
    """
    if hasattr(annotation, "__metadata__"):
        return resolve_annotation(
            annotation.__origin__, (*metadata, *_flatten(annotation.__metadata__))
        )

    origin = typing.get_origin(annotation)

    if _is_union(origin):
        return _resolve_union(annotation, metadata)

    if origin is list:
        args = typing.get_args(annotation)
        # NB: `metadata` deliberately does not reach the item -- min_length /
        # max_length on a list field bound the list, not each element.
        item = (
            resolve_annotation(args[0]).node
            if args
            else UnknownNode("bare `list` with no item type")
        )
        c = _meta_constraints(metadata)
        return ResolvedField(
            ListNode(item, c.get("min_length"), c.get("max_length")), nullable=False
        )

    if origin is Literal:
        return ResolvedField(LiteralNode(typing.get_args(annotation)), nullable=False)

    if isinstance(annotation, type):
        return _resolve_class(annotation, metadata)

    return ResolvedField(
        UnknownNode(f"{annotation!r} (not a class this resolver has a rule for)"),
        nullable=False,
    )


def fields_of(model: type[BaseModel]) -> list[FieldSpec]:
    """All fields of `model`, declared and computed, via `resolve_annotation`."""
    out = []
    for name, info in model.model_fields.items():
        r = resolve_annotation(info.annotation, tuple(info.metadata))
        out.append(
            FieldSpec(
                name,
                info.alias or name,
                r.node,
                info.is_required(),
                r.nullable,
            )
        )
    for name, computed in model.model_computed_fields.items():
        # `model_dump(mode="json")` emits these, so a schema without them would
        # strip them off any payload it parses. Never required: pydantic derives
        # the value, so a payload may legitimately omit it. Never *validated*
        # either -- pydantic rejects a wrong-but-well-formed value by recomputing
        # it, which would mean reimplementing mex-common's identifier derivation.
        r = resolve_annotation(computed.return_type)
        out.append(
            FieldSpec(
                name,
                computed.alias or name,
                r.node,
                required=False,
                nullable=r.nullable,
            )
        )
    return out
