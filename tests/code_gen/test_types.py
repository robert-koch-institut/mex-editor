from pydantic import BaseModel, Field

from mex.editor.code_gen.models import ScalarNode, UnionNode
from mex.editor.code_gen.types import fields_of
from tests.code_gen.helpers import generate
from tests.code_gen.sample_models import UnionWithFieldConstraint


def test_a_constraint_on_a_union_field_reaches_every_member() -> None:
    [spec] = [f for f in fields_of(UnionWithFieldConstraint) if f.py_name == "code"]
    assert isinstance(spec.node, UnionNode)
    members = [m for m in spec.node.members if isinstance(m, ScalarNode)]
    assert len(members) == 2
    assert all(m.min_length == 4 for m in members), members
    # ...without clobbering each member's own pattern.
    assert len({m.pattern for m in members}) == 2


def test_list_bounds_stay_on_the_list_and_do_not_leak_into_its_items() -> None:
    class HasTags(BaseModel):
        tags: list[str] = Field(min_length=1, max_length=5)

    source = generate([HasTags])["thing.ts"]
    [line] = [line for line in source.splitlines() if line.strip().startswith("tags:")]
    assert line.strip() == "tags: z.array(z.string()).min(1).max(5),"
