from collections.abc import Sequence
from typing import Any

import reflex as rx
from reflex.base import BaseModel
from reflex.components import Component
from reflex.components.radix.themes.components.select import (
    HighLevelSelect,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectRoot,
    SelectTrigger,
)
from reflex.vars.base import Var


class ValueLabelSelectItem(BaseModel):
    """Items for ValueLabelHighLevelSelect that contain value and label."""

    value: str
    label: str


class ValueLabelHighLevelSelect(HighLevelSelect):
    """High level wrapper for the Select component."""

    @classmethod
    def create_value_label_select(
        cls,
        items: Sequence[ValueLabelSelectItem] | Var[Sequence[ValueLabelSelectItem]],
        **props,  # noqa: ANN003
    ) -> Component:
        """Create a select component. THIS IS COPY PASTE FROM HighLevelSelect!

        Args:
            items: The items (with "label" and "value") of the select.
            **props: Additional properties to apply to the select component.

        Returns:
            The select component.
        """
        trigger_prop_list = [
            "id",
            "placeholder",
            "variant",
            "radius",
            "width",
            "flex_shrink",
            "custom_attrs",
        ]

        content_props = {
            prop: props.pop(prop)
            for prop in ["high_contrast", "position"]
            if prop in props
        }

        trigger_props = {
            prop: props.pop(prop) for prop in trigger_prop_list if prop in props
        }

        color_scheme = props.pop("color_scheme", None)

        if color_scheme is not None:
            content_props["color_scheme"] = color_scheme
            trigger_props["color_scheme"] = color_scheme

        label = props.pop("label", None)

        child: list[Any] = []
        if isinstance(items, Var):
            child = [
                rx.foreach(
                    items,
                    lambda item: SelectItem.create(
                        item.label,
                        value=item.value,
                    ),
                )
            ]
        else:
            child = [
                SelectItem.create(
                    item.label,
                    value=item.value,
                )
                for item in items
            ]

        return SelectRoot.create(
            SelectTrigger.create(
                **trigger_props,
            ),
            SelectContent.create(
                SelectGroup.create(
                    SelectLabel.create(label) if label is not None else "",
                    *child,
                ),
                **content_props,
            ),
            **props,
        )


value_label_select = ValueLabelHighLevelSelect.create_value_label_select
