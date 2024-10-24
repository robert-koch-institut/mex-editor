from pydantic import BaseModel

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import AnyExtractedModel
from mex.editor.edit.models import EditableField, EditablePrimarySource
from mex.editor.state import State
from mex.editor.transform import render_any_value, render_model_title


class _BackendSearchResponse(BaseModel):
    total: int
    items: list[AnyExtractedModel]


class EditState(State):
    """State for the edit component."""

    fields: list[EditableField] = []
    item_title: str = ""

    def refresh(self) -> None:
        """Refresh the search results."""
        # TODO: use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()

        # TODO: use a specialized extracted-item search method
        response = connector.request(
            "GET", f"extracted-item?stableTargetId={self.item_id}"
        )
        items = _BackendSearchResponse.model_validate(response).items
        self.fields = self.extracted_to_fields(items)

        # TODO: use title of merged item instead of title of first item
        self.item_title = render_model_title(items[0])

    @staticmethod
    def extracted_to_fields(models: list[AnyExtractedModel]) -> list[EditableField]:
        """Convert a list of extracted models into editable field models."""
        fields_by_name: dict[str, EditableField] = {}
        for model in models:
            model_dump = model.model_dump()
            for field_name in model.model_fields:
                editable_field = fields_by_name.setdefault(
                    field_name, EditableField(name=field_name, primary_sources=[])
                )
                value = model_dump[field_name]
                if not value:
                    continue
                if not isinstance(value, list):
                    value = [value]
                editable_field.primary_sources.append(
                    EditablePrimarySource(
                        name=model.hadPrimarySource,
                        editable_values=[render_any_value(v) for v in value],
                    )
                )
        return list(fields_by_name.values())
