from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel

from mex.common.models import AdditiveRule, ExtractedData, MergedItem
from mex.common.models.base.rules import RuleSet
from mex.editor.code_gen.models import (
    EnumDef,
    EnumRef,
    ListNode,
    ModelDef,
    ObjectRef,
    SchemaIndex,
    UnionNode,
)
from mex.editor.code_gen.types import fields_of

if TYPE_CHECKING:
    from mex.editor.code_gen.models import Bundle, Node

# Framework plumbing, not a real shared domain shape -- never worth factoring
# out as its own def. Held as mex-common's own classes rather than a copy of
# their names, so a rename upstream is a hard import error, not a silent miss.
# None of these is `__bases__[0]` for today's six families (mex-common declares
# the domain base first), but that ordering is not ours to rely on.
_NON_DOMAIN_BASES = (BaseModel, ExtractedData, MergedItem, AdditiveRule, RuleSet)

# A base shared by fewer models than this isn't worth its own def.
_MIN_MODELS_PER_BASE = 2


def referenced_classes(node: Node) -> list[type[BaseModel | Enum]]:
    """The model/enum classes `node` points at (through a list/union, if any)."""
    if isinstance(node, (ObjectRef, EnumRef)):
        return [node.cls]
    if isinstance(node, ListNode):
        return referenced_classes(node.item)
    if isinstance(node, UnionNode):
        return [c for m in node.members for c in referenced_classes(m)]
    return []


class _Registrar:
    """Registers model/enum classes into a `SchemaIndex`.

    Follows every field that references another class and records the
    reference graph (`edges`) as it goes.
    """

    def __init__(self, index: SchemaIndex) -> None:
        """Register into the given (usually empty) `index`."""
        self.index = index
        self.edges: dict[str, set[str]] = {}

    def _check_collision(self, name: str, cls: type) -> None:
        """Raise if `name` is already registered to a different class."""
        existing = self.index.defs.get(name)
        if existing is not None and existing.cls is not cls:
            msg = f"Two different classes named {name!r}: {existing.cls!r} vs {cls!r}"
            raise ValueError(msg)

    def register_model(self, cls: type[BaseModel]) -> str:
        name = cls.__name__
        if name in self.index.defs:
            self._check_collision(name, cls)
            return name
        specs = fields_of(cls)
        self.index.defs[name] = ModelDef(cls=cls, fields=specs)
        self.edges[name] = set()
        for spec in specs:
            for ref in referenced_classes(spec.node):
                self.edges[name].add(self.register(ref))
        return name

    def register(self, cls: type[BaseModel | Enum]) -> str:
        """Register `cls` as whichever kind of def it is."""
        if issubclass(cls, Enum):
            return self.register_enum(cls)
        return self.register_model(cls)

    def register_enum(self, cls: type[Enum]) -> str:
        name = cls.__name__
        if name in self.index.defs:
            self._check_collision(name, cls)
            return name
        self.index.defs[name] = EnumDef(cls=cls)
        self.edges.setdefault(name, set())
        return name


def _shared_base(model: type[BaseModel]) -> type[BaseModel] | None:
    """Return the domain base `model` might share with a sibling, if any.

    mex-common composes Extracted/Merged as `class ExtractedX(BaseX,
    ExtractedData)`, declaring the domain base first. Private (leading "_") and
    framework bases are skipped: two unrelated private bases can legitimately
    share a name, as mex-common's per-module `_BaseRuleSet` does.
    """
    if not model.__bases__:
        return None
    base = model.__bases__[0]
    if not (isinstance(base, type) and issubclass(base, BaseModel)):
        return None
    if base in _NON_DOMAIN_BASES or base.__name__.startswith("_"):
        return None
    return base if base.model_fields else None


def _factor_bases(index: SchemaIndex, bundle: Bundle, reg: _Registrar) -> None:
    """Give a base shared by several of the bundle's models its own def.

    Only a base shared by at least `_MIN_MODELS_PER_BASE` of THIS bundle's own
    models is worth factoring out; one used by a single model is not.
    """
    groups: dict[type[BaseModel], list[str]] = {}
    for model in bundle.models:
        if (base := _shared_base(model)) is not None:
            groups.setdefault(base, []).append(model.__name__)
    for base_cls, names in groups.items():
        if len(names) < _MIN_MODELS_PER_BASE:
            continue
        base_name = reg.register_model(base_cls)
        base_entry = index.defs[base_name]
        if not isinstance(base_entry, ModelDef):
            continue
        base_fields = {f.py_name: f for f in base_entry.fields}
        for name in names:
            entry = index.defs[name]
            if isinstance(entry, ModelDef):
                # Drop a field only when it is identical to the base's. A
                # subclass that NARROWS one (say, adds a pattern) has to keep
                # re-declaring it -- `.extend()` overrides correctly, but only
                # for fields we actually emit. Comparing the whole FieldSpec is
                # safe now that it carries nothing the generator ignores.
                remaining = [f for f in entry.fields if base_fields.get(f.py_name) != f]
                index.defs[name] = ModelDef(
                    cls=entry.cls, fields=remaining, extends=base_name
                )
                reg.edges[name].add(base_name)


def build_schema_index(bundles: list[Bundle]) -> SchemaIndex:
    """Collect every def reachable from `bundles`' requested models.

    Walks the models recursively and collects every model/enum into one
    deduplicated `SchemaIndex`, recording which bundle(s) use each one --
    entirely from Python types, never from JSON schema.
    """
    index = SchemaIndex()
    reg = _Registrar(index)
    roots = {b.name: [reg.register_model(m) for m in b.models] for b in bundles}
    for bundle in bundles:
        _factor_bases(index, bundle, reg)
    # Propagate "which bundle uses this def" through the reference graph.
    for bundle in bundles:
        stack, seen = list(roots[bundle.name]), set()
        while stack:
            name = stack.pop()
            if name in seen:
                continue
            seen.add(name)
            index.bundles_using_def.setdefault(name, set()).add(bundle.name)
            stack.extend(reg.edges.get(name, ()))
    return index
