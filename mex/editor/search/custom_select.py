from typing import Any

import reflex as rx
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


class CustomHighLevelSelect(HighLevelSelect):
    """High level wrapper for the Select component."""

    @classmethod
    def create_value_label_select(
        cls,
        items: list[dict[str, str]] | Var[list[dict[str, str]]],
        **props,  # noqa: ANN003
    ) -> Component:
        """Create a select component. THIS IS COPY PASTE FROM HighLevelSelect!

        Args:
            items: The items (as dict with "label" and "value") of the select.
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
                        item["label"],
                        value=item["value"],
                    ),
                )
            ]
        else:
            child = [
                SelectItem.create(
                    item["label"],
                    value=item["value"],
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


custom_select = CustomHighLevelSelect.create_value_label_select
