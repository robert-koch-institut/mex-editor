"""Python type IR -> TypeScript interfaces/type-aliases."""
from __future__ import annotations
import json
from .pytypes import EnumRef, ListNode, LiteralNode, Node, ObjectRef, ScalarNode, UnionNode
from .schema_collect import DefEntry, EnumDef
from .ts_writer import render_interface, render_type_alias


def ts_type_for_node(node: Node) -> str:
    if isinstance(node, (ObjectRef, EnumRef)):
        return node.cls.__name__
    if isinstance(node, LiteralNode):
        return " | ".join(_lit(v) for v in node.values)
    if isinstance(node, ListNode):
        inner = ts_type_for_node(node.item)
        return f"({inner})[]" if " | " in inner else f"{inner}[]"
    if isinstance(node, UnionNode):
        return " | ".join(sorted({ts_type_for_node(m) for m in node.members}))
    if isinstance(node, ScalarNode):
        return "boolean" if node.py_type is bool else "number" if node.py_type in (int, float) else "string"
    return "unknown"


def _lit(v: object) -> str:
    if isinstance(v, str):
        return json.dumps(v)
    return "true" if v is True else "false" if v is False else str(v)


def _clean(text: str | None) -> str | None:
    return " ".join(text.split()).replace("*/", "* /") if text else None


def render_def_interface(name: str, entry: DefEntry) -> str:
    if isinstance(entry, EnumDef):
        return render_type_alias(name, [json.dumps(m.value) for m in entry.cls], _clean((entry.cls.__doc__ or "").strip()))

    fields = []
    for f in entry.fields:
        fixed_literal = isinstance(f.node, LiteralNode) and len(f.node.values) == 1
        optional = False if fixed_literal else not (f.required and not f.nullable)
        fields.append({"name": f.alias, "optional": optional, "ts_type": ts_type_for_node(f.node), "doc": _clean(f.description)})
    return render_interface(name, fields, entry.extends, _clean((entry.cls.__doc__ or "").strip()))
