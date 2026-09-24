"""Written by Claude (Anthropic).

Walks a list of `Bundle`s via `pytypes` and builds a deduplicated
registry of every def (model or enum) reachable from them, plus which
bundle(s) use each one -- entirely from Python types, no JSON schema."""
# mypy: ignore-errors
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel
from .bundle import Bundle
from .pytypes import EnumRef, FieldSpec, ListNode, Node, ObjectRef, UnionNode, fields_of

# First-declared bases that are framework plumbing, not a real shared
# shape -- never worth factoring out as their own def.
_NON_DOMAIN_BASES = {"BaseModel", "ExtractedData", "MergedItem", "RuleSet"}


@dataclass(frozen=True)
class ModelDef:
    """A def backed by a pydantic model. `extends` is set when this def's
    fields were factored out of a base shared with a sibling model in the
    same bundle (see `_factor_bases`) -- `fields` then excludes whatever
    the base already covers."""

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
    """Everything generators need: every def, which bundle "owns" it
    (used by exactly one) or shares it (used by more than one), and which
    defs are each bundle's own requested root/entity models."""

    defs: dict[str, DefEntry] = field(default_factory=dict)
    roots: dict[str, list[str]] = field(default_factory=dict)
    bundles_using_def: dict[str, set[str]] = field(default_factory=dict)

    def shared_defs(self) -> set[str]:
        """Def names referenced by more than one bundle."""
        return {n for n, u in self.bundles_using_def.items() if len(u) > 1}

    def owning_bundle(self, def_name: str) -> str | None:
        """The single bundle that owns `def_name`, or None if it's shared."""
        u = self.bundles_using_def.get(def_name, set())
        return next(iter(u)) if len(u) == 1 else None


def referenced_def_names(node: Node) -> set[str]:
    """Def names `node` points at directly (through a list/union, if any)."""
    if isinstance(node, (ObjectRef, EnumRef)):
        return {node.cls.__name__}
    if isinstance(node, ListNode):
        return referenced_def_names(node.item)
    if isinstance(node, UnionNode):
        return {n for m in node.members for n in referenced_def_names(m)}
    return set()


class _Registrar:
    """Registers model/enum classes into a `SchemaIndex`, following every
    field that references another class and recording the reference graph
    (`edges`) as it goes."""

    def __init__(self, index: SchemaIndex) -> None:
        self.index = index
        self.edges: dict[str, set[str]] = {}

    def _check_collision(self, name: str, cls: type) -> None:
        existing = self.index.defs.get(name)
        if existing is not None and existing.cls is not cls:
            raise ValueError(f"Two different classes named {name!r}: {existing.cls!r} vs {cls!r}")

    def register_model(self, cls: type[BaseModel]) -> str:
        name = cls.__name__
        if name in self.index.defs:
            self._check_collision(name, cls)
            return name
        specs = fields_of(cls)
        self.index.defs[name] = ModelDef(cls=cls, fields=specs)
        self.edges[name] = set()
        for spec in specs:
            refs = referenced_def_names(spec.node)
            self.edges[name] |= refs
            for ref in refs:
                self._register_referenced(spec.node, ref)
        return name

    def _register_referenced(self, node: Node, expected: str) -> None:
        if isinstance(node, ObjectRef) and node.cls.__name__ == expected:
            self.register_model(node.cls)
        elif isinstance(node, EnumRef) and node.cls.__name__ == expected:
            self.register_enum(node.cls)
        elif isinstance(node, ListNode):
            self._register_referenced(node.item, expected)
        elif isinstance(node, UnionNode):
            for m in node.members:
                self._register_referenced(m, expected)

    def register_enum(self, cls: type[Enum]) -> str:
        name = cls.__name__
        if name in self.index.defs:
            self._check_collision(name, cls)
            return name
        self.index.defs[name] = EnumDef(cls=cls)
        self.edges.setdefault(name, set())
        return name


def _shared_base(model: type[BaseModel]) -> type[BaseModel] | None:
    # mex-common composes Extracted/Merged as class ExtractedX(BaseX,
    # ExtractedData) -- the domain base is declared first. Skip private
    # (leading "_") and framework bases: two unrelated private bases can
    # legitimately share a name (mex-common has a per-module _BaseRuleSet).
    if not model.__bases__:
        return None
    base = model.__bases__[0]
    if not (isinstance(base, type) and issubclass(base, BaseModel)):
        return None
    if base is BaseModel or base.__name__ in _NON_DOMAIN_BASES or base.__name__.startswith("_"):
        return None
    return base if base.model_fields else None


def _factor_bases(index: SchemaIndex, bundle: Bundle, reg: _Registrar) -> None:
    # Only factor out a base shared by >=2 of THIS bundle's own models --
    # a base used by just one model isn't worth a separate def.
    groups: dict[type[BaseModel], list[str]] = {}
    for model in bundle.models:
        if (base := _shared_base(model)) is not None:
            groups.setdefault(base, []).append(model.__name__)
    for base_cls, names in groups.items():
        if len(names) < 2:
            continue
        base_name = reg.register_model(base_cls)
        base_fields = {f.py_name for f in index.defs[base_name].fields}
        for name in names:
            entry = index.defs[name]
            if isinstance(entry, ModelDef):
                remaining = [f for f in entry.fields if f.py_name not in base_fields]
                index.defs[name] = ModelDef(cls=entry.cls, fields=remaining, extends=base_name)
                reg.edges[name].add(base_name)


def build_schema_index(bundles: list[Bundle]) -> SchemaIndex:
    """Collect every model/enum reachable from `bundles`' requested models
    (recursively) into one `SchemaIndex`, ready for any generator."""
    index = SchemaIndex()
    reg = _Registrar(index)
    for bundle in bundles:
        index.roots[bundle.name] = [reg.register_model(m) for m in bundle.models]
    for bundle in bundles:
        _factor_bases(index, bundle, reg)
    # Propagate "which bundle uses this def" through the reference graph.
    for bundle in bundles:
        stack, seen = list(index.roots[bundle.name]), set()
        while stack:
            name = stack.pop()
            if name in seen:
                continue
            seen.add(name)
            index.bundles_using_def.setdefault(name, set()).add(bundle.name)
            stack.extend(reg.edges.get(name, ()))
    return index
