"""AI-generated codegen module (Claude). Kept compact, not optimized for
human readability -- the *output* it produces is what should stay
readable, not this file.

Python type IR -> Angular Signal Forms validators. Two relaxations:
`EnumDef` validators take `SchemaPath<string>` (not the narrower enum
type) so a loosely-typed string field can reuse them; a `ModelDef` with
exactly one required scalar field (e.g. Text.value, Link.url) also accepts
a bare string via `applyWhenValue`, checked with that field's own rules.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from .patterns import PatternRegistry
from .pytypes import EnumRef, FieldSpec, ListNode, LiteralNode, Node, ObjectRef, ScalarNode, UnionNode
from .schema_collect import DefEntry, EnumDef, ModelDef
from .ts_types import ts_type_for_node
from .ts_writer import render_enum_validator, render_forgiving_aggregator, render_function, render_tree_aggregator


@dataclass
class GenResult:
    item_function: str | None = None
    field_function: str = ""
    signals_forms_fns: set[str] = field(default_factory=set)
    runtime_fns: set[str] = field(default_factory=set)
    pattern_names: set[str] = field(default_factory=set)
    referenced_defs: set[str] = field(default_factory=set)


def _pascal(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def _describe(subject: str, notes: list[str], fallback: str | None = None) -> str:
    notes = notes or ([fallback] if fallback else [])
    return f"Validates that {subject} " + "; ".join(notes) + "." if notes else ""


def _constraints(node: Node, patterns: PatternRegistry, r: GenResult, body: list[str], notes: list[str], field_name: str | None = None) -> None:
    if isinstance(node, ObjectRef):
        ref = node.cls.__name__
        r.referenced_defs.add(ref)
        body.append(f"validate{ref}(path);")
        notes.append(f"validated with the `{ref}` rules (a plain string is also accepted where `{ref}` allows it)")
        return
    if isinstance(node, EnumRef):
        ref = node.cls.__name__
        r.referenced_defs.add(ref)
        body.append(f"validate{ref}(path);")
        notes.append(f"must be one of the values allowed by `{ref}`")
        return
    if isinstance(node, UnionNode):
        scalars = [m for m in node.members if isinstance(m, ScalarNode)]
        if len(scalars) != len(node.members) or not scalars:
            body.append("// TODO: review this field manually -- union includes non-scalar members")
            notes.append("NOT YET VALIDATED -- union includes model/enum members, needs manual review")
            return
        if any(m.pattern is None for m in scalars):
            return  # a branch accepts any string -> union is unconstrained
        names = list(dict.fromkeys(patterns.name_for(m.pattern, m.leaf_cls.__name__, field_name) for m in scalars))
        r.pattern_names |= set(names)
        body.append(f"anyOfPatternValidator(path, [{', '.join(names)}], 'invalidFormat', false);")
        notes.append(f"must match at least one of these formats: {', '.join(names)}")
        r.runtime_fns.add("anyOfPatternValidator")
        return
    if isinstance(node, ScalarNode):
        if node.pattern:
            name = patterns.name_for(node.pattern, node.leaf_cls.__name__, field_name)
            r.pattern_names.add(name)
            body.append(f"pattern(path, new RegExp({name}), {{ message: 'pattern' }});")
            notes.append(f"must match the `{name}` regular expression")
            r.signals_forms_fns.add("pattern")
        elif node.format == "email":
            body.append("email(path, { message: 'email' });")
            notes.append("must be a valid email address")
            r.signals_forms_fns.add("email")
        if node.py_type in (int, float):
            if node.minimum is not None:
                body.append(f"min(path, {node.minimum}, {{ message: 'min' }});")
                notes.append(f"must be >= {node.minimum}")
                r.signals_forms_fns.add("min")
            if node.maximum is not None:
                body.append(f"max(path, {node.maximum}, {{ message: 'max' }});")
                notes.append(f"must be <= {node.maximum}")
                r.signals_forms_fns.add("max")
        if node.py_type is str and not node.pattern:
            if node.min_length is not None:
                body.append(f"minLength(path, {node.min_length}, {{ message: 'minLength' }});")
                notes.append(f"must be at least {node.min_length} character(s) long")
                r.signals_forms_fns.add("minLength")
            if node.max_length is not None:
                body.append(f"maxLength(path, {node.max_length}, {{ message: 'maxLength' }});")
                notes.append(f"must be at most {node.max_length} character(s) long")
                r.signals_forms_fns.add("maxLength")
        return
    body.append("// TODO: review this field manually -- unrecognized Python type")
    notes.append("NOT YET VALIDATED -- unrecognized Python type, needs manual review")


def generate_field_validator(owner: str, spec: FieldSpec, patterns: PatternRegistry) -> GenResult:
    fn_name = f"validate{owner}_{_pascal(spec.py_name)}"
    path_type = ts_type_for_node(spec.node)
    r = GenResult()
    node = spec.node

    if isinstance(node, ListNode):
        body, notes = [], []
        if spec.required:
            body.append("required(path, { message: 'required' });")
            notes.append("must be present")
            r.signals_forms_fns.add("required")
        if node.min_length is not None:
            body.append(f"minLength(path, {node.min_length}, {{ message: 'minItems' }});")
            notes.append(f"must contain at least {node.min_length} item(s)")
            r.signals_forms_fns.add("minLength")
        if node.max_length is not None:
            body.append(f"maxLength(path, {node.max_length}, {{ message: 'maxItems' }});")
            notes.append(f"must contain at most {node.max_length} item(s)")
            r.signals_forms_fns.add("maxLength")
        if isinstance(node.item, (ObjectRef, EnumRef)):
            ref = node.item.cls.__name__
            r.referenced_defs.add(ref)
            body.append(f"applyEach(path, validate{ref});")
            notes.append(f"each item is validated with the `{ref}` rules")
            r.signals_forms_fns.add("applyEach")
        else:
            item_body, item_notes = [], []
            _constraints(node.item, patterns, r, item_body, item_notes, spec.py_name)
            item_body = item_body or ["// no additional validation beyond the field's own type check"]
            item_notes = item_notes or ["only checked against its own type, no extra constraints"]
            item_fn = f"{fn_name}Item"
            r.item_function = render_function(item_fn, ts_type_for_node(node.item), item_body, _describe(f"each `{spec.py_name}` item", item_notes))
            body.append(f"applyEach(path, {item_fn});")
            notes.append("each item is checked individually (see above)")
            r.signals_forms_fns.add("applyEach")
        r.field_function = render_function(fn_name, path_type, body, _describe(f"`{spec.py_name}`", notes, "no constraints on the list itself"))
        return r

    body, notes = [], []
    if spec.required:
        body.append("required(path, { message: 'required' });")
        notes.append("must be present")
        r.signals_forms_fns.add("required")
    _constraints(node, patterns, r, body, notes, spec.py_name)
    body = body or ["// no additional validation beyond the field's own type check"]
    r.field_function = render_function(fn_name, path_type, body, _describe(f"`{spec.py_name}`", notes, "only checked against its own type, no extra constraints"))
    return r


def _primary_scalar_field(entry: ModelDef) -> FieldSpec | None:
    """Field a bare string collapses onto in the 'forgiving' variant --
    only when there's exactly one required scalar field, rest optional."""
    required = [f for f in entry.fields if f.required and not isinstance(f.node, LiteralNode)]
    if len(required) != 1 or not isinstance(required[0].node, ScalarNode):
        return None
    return required[0]


def generate_def_validator(def_name: str, entry: DefEntry, patterns: PatternRegistry) -> GenResult:
    if isinstance(entry, EnumDef):
        r = GenResult()
        values = [f"'{m.value}'" for m in entry.cls]
        r.runtime_fns.add("enumValidator")
        doc = f"Validates that the value is one of: {', '.join(values)}. Takes a plain `string` path rather than `{def_name}` so a loosely-typed string field can be checked with these same rules too."
        r.field_function = render_enum_validator(def_name, values, doc)
        return r

    combined = GenResult()
    calls, parts = [], []
    if entry.extends:
        combined.referenced_defs.add(entry.extends)
        calls += [f"// fields shared with other {entry.extends} subtypes", f"validate{entry.extends}(path);"]
    for spec in entry.fields:
        if isinstance(spec.node, LiteralNode):
            continue
        fr = generate_field_validator(def_name, spec, patterns)
        combined.signals_forms_fns |= fr.signals_forms_fns
        combined.runtime_fns |= fr.runtime_fns
        combined.pattern_names |= fr.pattern_names
        combined.referenced_defs |= fr.referenced_defs
        if fr.item_function:
            parts.append(fr.item_function)
        parts.append(fr.field_function)
        calls.append(f"validate{def_name}_{_pascal(spec.py_name)}(path.{spec.alias});")

    primary = None if entry.extends else _primary_scalar_field(entry)
    if primary is not None:
        primary_fn = f"validate{def_name}_{_pascal(primary.py_name)}"
        doc = (
            f"Validates every field of `{def_name}`. Also accepts a plain string in place of the full object: "
            f"`{def_name}` has exactly one required field (`{primary.py_name}`), so a bare string is treated as "
            f"shorthand for `{{ {primary.py_name}: <that string> }}` and checked with `{primary.py_name}`'s own rules."
        )
        combined.signals_forms_fns.add("applyWhenValue")
        aggregator = render_forgiving_aggregator(def_name, primary_fn, calls, doc)
    else:
        doc = f"Validates every field of `{def_name}`" + (f" (including the fields inherited from `{entry.extends}`)" if entry.extends else "") + "."
        aggregator = render_tree_aggregator(def_name, calls, doc)

    combined.field_function = "".join([*parts, aggregator])
    return combined
