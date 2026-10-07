import json
import re
from enum import Enum
from typing import TYPE_CHECKING

from mex.editor.code_gen.models import (
    DefEntry,
    EnumDef,
    EnumRef,
    ListNode,
    LiteralNode,
    Node,
    ObjectRef,
    ScalarNode,
    UnionNode,
    UnknownNode,
    ZodResult,
)

if TYPE_CHECKING:
    from mex.editor.code_gen.patterns import PatternRegistry


def jsdoc(text: str) -> str:
    """Render `text` as a `/** ... */` block comment.

    Every exported declaration gets one of these, never a `//` line comment.
    """
    return f"/**\n * {text}\n */\n"


def _chain(*constraints: tuple[float | None, str]) -> str:
    """Join the constraints that are set into a chain like `.min(1).max(5)`."""
    return "".join(f".{method}({v})" for v, method in constraints if v is not None)


def _scalar_zod(
    node: ScalarNode, patterns: PatternRegistry, field_name: str | None, r: ZodResult
) -> str:
    """Render a `ScalarNode` as its Zod expression.

    Base type first, then whatever constraints this scalar carries.
    """
    if node.py_type is bool:
        return "z.boolean()"
    if node.py_type in (int, float):
        # .min()/.max() are Zod's inclusive gte/lte; exclusive bounds have to
        # stay exclusive or the browser would accept what the backend rejects.
        base = "z.int()" if node.py_type is int else "z.number()"
        return base + _chain(
            (node.minimum, "min"),
            (node.maximum, "max"),
            (node.exclusive_minimum, "gt"),
            (node.exclusive_maximum, "lt"),
        )
    base = "z.string()"
    if node.pattern:
        name = patterns.name_for(node.pattern, node.leaf_cls.__name__, field_name)
        r.pattern_names.add(name)
        base += f".regex(new RegExp({name}))"
    elif node.format:
        # No pattern to fall back on, so the format is the only constraint there
        # was -- and this generator has no rule for turning one into Zod.
        r.unknowns.append(f"JSON Schema format {node.format!r} has no Zod rule")
    return base + _chain((node.min_length, "min"), (node.max_length, "max"))


_TS_IDENTIFIER = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")


def _object_key(alias: str) -> str:
    """`alias` as a TS object key, quoted only when it has to be.

    Reserved words (`class`, `if`) are legal property names unquoted; only
    punctuation and a leading digit force quoting.
    """
    if _TS_IDENTIFIER.fullmatch(alias):
        return alias
    return json.dumps(alias)


def _literal_value(value: object) -> str:
    """Render one literal value the way TypeScript spells it.

    `json.dumps` gets every JSON scalar right, including `true`/`false`/`null`,
    which Python's `repr` would spell `True`/`False`/`None`.
    """
    if isinstance(value, Enum):
        value = value.value
    try:
        return json.dumps(value)
    except TypeError:
        return json.dumps(str(value))


def _literal_zod(node: LiteralNode) -> str:
    """Render a `LiteralNode` as its Zod expression.

    Zod 4 accepts a list of members; a single value stays a plain
    `z.literal(x)`, which is what every `$type` discriminator emits.
    """
    values = ", ".join(_literal_value(v) for v in node.values)
    if len(node.values) == 1:
        return f"z.literal({values})"
    return f"z.literal([{values}])"


def _union_zod(
    node: UnionNode, patterns: PatternRegistry, field_name: str | None, r: ZodResult
) -> str:
    """Render a `UnionNode` as its Zod expression.

    A union whose members are all patterned scalars collapses to one regex
    alternative per distinct pattern, rather than a union of object schemas.
    """
    scalars = [m for m in node.members if isinstance(m, ScalarNode)]
    if (
        len(scalars) == len(node.members)
        and scalars
        and all(m.pattern for m in scalars)
    ):
        # Union of patterned scalars (e.g. YearMonthDay | YearMonth |
        # Year) -> try each regex in turn.
        parts = list(
            dict.fromkeys(_scalar_zod(m, patterns, field_name, r) for m in scalars)
        )
    else:
        parts = [zod_for_node(m, patterns, r, field_name) for m in node.members]
    return parts[0] if len(parts) == 1 else f"z.union([{', '.join(parts)}])"


def zod_for_node(
    node: Node, patterns: PatternRegistry, r: ZodResult, field_name: str | None = None
) -> str:
    """The Zod expression for one field's resolved node (recursive).

    A reference to another model is emitted as that model's schema, strictly --
    no relaxation like also accepting a bare id string in its place.
    """
    if isinstance(node, (ObjectRef, EnumRef)):
        r.def_refs.add(node.cls.__name__)
        return f"{node.cls.__name__}Schema"
    if isinstance(node, LiteralNode):
        return _literal_zod(node)
    if isinstance(node, ListNode):
        item = zod_for_node(node.item, patterns, r, field_name)
        bounds = _chain((node.min_length, "min"), (node.max_length, "max"))
        return f"z.array({item}){bounds}"
    if isinstance(node, UnionNode):
        return _union_zod(node, patterns, field_name, r)
    if isinstance(node, ScalarNode):
        return _scalar_zod(node, patterns, field_name, r)
    if isinstance(node, UnknownNode):
        r.unknowns.append(node.description)
    return "z.unknown()"


def render_zod_schema(
    name: str, entry: DefEntry, patterns: PatternRegistry
) -> ZodResult:
    """Render one def as its `{name}Schema` const plus its `{name}` type alias.

    Each gets its own `/** */` doc comment. Pure string building: which file the
    block lands in, and what that file imports, is `zod_generator`'s business.
    """
    r = ZodResult()

    if isinstance(entry, EnumDef):
        members = [m.value for m in entry.cls]
        values = ", ".join(_literal_value(v) for v in members)
        # z.enum is string-only; anything else has to be a union of literals or
        # the generated schema would demand "1" where pydantic accepts 1.
        if all(isinstance(v, str) for v in members):
            schema = f"z.enum([{values}])"
        else:
            schema = f"z.literal([{values}])"
        r.code = (
            f"{jsdoc(f'Zod schema for the {name} enum.')}"
            f"export const {name}Schema = {schema};\n\n"
            f"{jsdoc(f'TypeScript type inferred from {name}Schema.')}"
            f"export type {name} = z.infer<typeof {name}Schema>;\n\n"
        )
        return r

    fields: list[str] = []
    for f in entry.fields:
        before = len(r.unknowns)
        z = zod_for_node(f.node, patterns, r, f.py_name)
        if len(r.unknowns) > before:
            # On its own line so the one-field-per-line shape of the output
            # (which render tests and `field_expr` rely on) is preserved.
            reasons = "; ".join(r.unknowns[before:])
            # Pydantic's own error text is multi-line; flatten it so the
            # comment cannot break out of its single line.
            one_line = " ".join(reasons.split())[:200]
            fields.append(f"  // UNRESOLVED -- accepts anything: {one_line}")
            r.unknowns[before:] = [f"{name}.{f.py_name}: {reasons}"]
        if f.nullable and not f.required:
            # pydantic dumps an unset Optional[X] field as explicit
            # JSON null, not a missing key -- .optional() alone only
            # covers "key absent", so a nullable-and-not-required
            # field needs BOTH allowed.
            z += ".nullish()"
        elif f.nullable:
            z += ".nullable()"
        elif not f.required:
            # A defaulted single-value literal (every `$type` discriminator) gets
            # .default() rather than .optional(): both accept the key being
            # absent, as pydantic does, but .default() keeps the *output* type
            # non-optional so TypeScript can still narrow a union on it.
            if isinstance(f.node, LiteralNode) and len(f.node.values) == 1:
                z += f".default({_literal_value(f.node.values[0])})"
            else:
                z += ".optional()"
        fields.append(f"  {_object_key(f.alias)}: {z},")

    body = "z.object({\n" + "\n".join(fields) + "\n})"
    doc = f"Zod schema for {name}."
    if entry.extends:
        r.def_refs.add(entry.extends)
        body = f"{entry.extends}Schema.extend({{\n" + "\n".join(fields) + "\n})"
        doc = f"Zod schema for {name} (extends {entry.extends})."

    r.code = (
        f"{jsdoc(doc)}"
        f"export const {name}Schema = {body};\n\n"
        f"{jsdoc(f'TypeScript type inferred from {name}Schema.')}"
        f"export type {name} = z.infer<typeof {name}Schema>;\n\n"
    )
    return r
