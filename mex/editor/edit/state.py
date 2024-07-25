import reflex as rx
from pydantic import BaseModel

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import AnyExtractedModel
from mex.editor.state import State
from mex.editor.transform import render


class EditablePrimarySource(rx.Base):
    """Model for describing the editor state for one primary source."""

    name: str
    values: list[str]


class EditableField(rx.Base):
    """Model for describing the editor state for a single field."""

    name: str
    values: list[EditablePrimarySource]


class _BackendSearchResponse(BaseModel):
    total: int
    items: list[AnyExtractedModel]


class EditState(State):
    """State for the edit component."""

    fields: list[EditableField]

    def refresh(self) -> None:
        """Refresh the search results."""
        # TODO: use the user auth for backend requests (stop-gap MX-1616)
        connector = BackendApiConnector.get()

        # TODO: use a specialized extracted-item search method
        response = connector.request(
            "GET", f"extracted-item?stableTargetId={self.item_id}"
        )
        self.fields = self.extracted_to_fields(
            _BackendSearchResponse.model_validate(response).items
        )

    @staticmethod
    def extracted_to_fields(models: list[AnyExtractedModel]) -> list[EditableField]:
        """Convert a list of extracted models into editable field models."""
        fields_by_name: dict[str, EditableField] = {}
        for model in models:
            model_dump = model.model_dump()
            for field_name in model.model_fields:
                editable_field = fields_by_name.setdefault(
                    field_name, EditableField(name=field_name, values=[])
                )
                value = model_dump[field_name]
                if not value:
                    continue
                if not isinstance(value, list):
                    value = [value]
                editable_field.values.append(
                    EditablePrimarySource(
                        name=model.hadPrimarySource,
                        values=[render(v) for v in value],
                    )
                )
        return list(fields_by_name.values())
