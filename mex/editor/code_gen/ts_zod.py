"""AI-generated codegen module (Claude). Compact by design.

Python type IR -> real Zod schemas (runtime-checkable, not just types).
Experimental: less field-shape coverage than ts_validators.py, but the
core (objects, arrays, unions of patterns, enums, extends, the
Text/Link-style "bare string OK" case) is real.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .patterns import PatternRegistry
from .pytypes import (
    EnumRef,
    ListNode,
    LiteralNode,
    Node,
    ObjectRef,
    ScalarNode,
    UnionNode,
)
from .schema_collect import DefEntry, EnumDef, ModelDef


@dataclass
class ZodResult:
    code: str = ""
    def_refs: set[str] = field(default_factory=set)
    pattern_names: set[str] = field(default_factory=set)


def _scalar_zod(
    node: ScalarNode, patterns: PatternRegistry, field_name: str | None, r: ZodResult
) -> str:
    base = (
        "z.boolean()"
        if node.py_type is bool
        else "z.number()"
        if node.py_type in (int, float)
        else "z.string()"
    )
    if node.py_type is str and node.pattern:
        name = patterns.name_for(node.pattern, node.leaf_cls.__name__, field_name)
        r.pattern_names.add(name)
        base += f".regex(new RegExp({name}))"
    elif node.format == "email":
        base += ".email()"
    if node.py_type is str:
        if node.min_length is not None:
            base += f".min({node.min_length})"
        if node.max_length is not None:
            base += f".max({node.max_length})"
    if node.py_type in (int, float):
        if node.minimum is not None:
            base += f".min({node.minimum})"
        if node.maximum is not None:
            base += f".max({node.maximum})"
    return base


def zod_for_node(
    node: Node, patterns: PatternRegistry, r: ZodResult, field_name: str | None = None
) -> str:
    if isinstance(node, (ObjectRef, EnumRef)):
        r.def_refs.add(node.cls.__name__)
        return f"{node.cls.__name__}Schema"
    if isinstance(node, LiteralNode):
        return " ".join(
            f'z.literal("{v}")' if isinstance(v, str) else f"z.literal({v!r})"
            for v in node.values
        )
    if isinstance(node, ListNode):
        arr = f"z.array({zod_for_node(node.item, patterns, r, field_name)})"
        if node.min_length is not None:
            arr += f".min({node.min_length})"
        if node.max_length is not None:
            arr += f".max({node.max_length})"
        return arr
    if isinstance(node, UnionNode):
        scalars = [m for m in node.members if isinstance(m, ScalarNode)]
        if (
            len(scalars) == len(node.members)
            and scalars
            and all(m.pattern for m in scalars)
        ):
            parts = list(
                dict.fromkeys(_scalar_zod(m, patterns, field_name, r) for m in scalars)
            )
            return parts[0] if len(parts) == 1 else f"z.union([{', '.join(parts)}])"
        return f"z.union([{', '.join(zod_for_node(m, patterns, r, field_name) for m in node.members)}])"
    if isinstance(node, ScalarNode):
        return _scalar_zod(node, patterns, field_name, r)
    return "z.unknown()"


def _primary_field(entry: ModelDef):
    required = [
        f for f in entry.fields if f.required and not isinstance(f.node, LiteralNode)
    ]
    return (
        required[0]
        if len(required) == 1 and isinstance(required[0].node, ScalarNode)
        else None
    )


def render_zod_schema(
    name: str, entry: DefEntry, patterns: PatternRegistry
) -> ZodResult:
    r = ZodResult()

    if isinstance(entry, EnumDef):
        values = ", ".join(f'"{m.value}"' for m in entry.cls)
        r.code = f"export const {name}Schema = z.enum([{values}]);\nexport type {name} = z.infer<typeof {name}Schema>;\n\n"
        return r

    fields = []
    for f in entry.fields:
        z = zod_for_node(f.node, patterns, r, f.py_name)
        if not (isinstance(f.node, LiteralNode) and len(f.node.values) == 1) and not (
            f.required and not f.nullable
        ):
            z += ".optional()"
        fields.append(f"  {f.alias}: {z},")

    body = "z.object({\n" + "\n".join(fields) + "\n})"
    if entry.extends:
        r.def_refs.add(entry.extends)
        body = f"{entry.extends}Schema.extend({{\n" + "\n".join(fields) + "\n})"

    primary = None if entry.extends else _primary_field(entry)
    if primary is not None:
        prim_zod = zod_for_node(primary.node, patterns, r, primary.py_name)
        body = f"z.union([{prim_zod}, {body}])"

    r.code = f"export const {name}Schema = {body};\nexport type {name} = z.infer<typeof {name}Schema>;\n\n"
    return r
