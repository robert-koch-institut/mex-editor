from typing import Annotated

from pydantic import BaseModel, Field

from tests.code_gen.helpers import generate


class NarrowBase(BaseModel):
    v: str
    shared: str


class NarrowSub1(NarrowBase):
    v: Annotated[str, Field(pattern=r"^\d+$")]
    only1: int = 0


class NarrowSub2(NarrowBase):
    only2: int = 0


def test_a_narrowed_base_field_is_re_declared_in_the_subclass() -> None:
    source = generate([NarrowSub1, NarrowSub2])["thing.ts"]
    block = source.split("export const NarrowSub1Schema")[1].split("});")[0]
    assert "NarrowBaseSchema.extend({" in block
    # The narrowed `v` must survive -- .extend() overrides, but only what we emit.
    assert "v: z.string().regex(" in block


def test_an_unchanged_base_field_is_not_re_declared() -> None:
    source = generate([NarrowSub1, NarrowSub2])["thing.ts"]
    block = source.split("export const NarrowSub1Schema")[1].split("});")[0]
    assert "shared:" not in block
    block2 = source.split("export const NarrowSub2Schema")[1].split("});")[0]
    assert "v:" not in block2
    assert "shared:" not in block2
