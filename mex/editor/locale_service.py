import re
from collections.abc import Sequence
from gettext import GNUTranslations
from importlib.resources import files
from pathlib import Path
from typing import Self, cast

from babel import Locale as BabelLocale

from mex.common.context import SingleSingletonStore
from mex.common.models import BaseModel

LOCALE_SERVICE_STORE = SingleSingletonStore["LocaleService"]()


class MExLocale(BaseModel):
    """Represents a locale with id and label."""

    id: str
    label: str
    filepath: Path


# TODO(ND): Move this to mex-common
def camelcase_to_title(value: str) -> str:
    """Convert a camelcase string into title-cased words splitted by space.

    Args:
        value: The camelcase string to convert.

    Returns:
        The converted string containing title-cased words splitted by space.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", " ", value).title()


class LocaleService:
    """A service singleton to control the current locale used by the app."""

    @classmethod
    def get(cls) -> Self:
        """Get singleton instance of the LocaleService.

        Returns:
            The LocaleService singleton.
        """
        return cast("Self", LOCALE_SERVICE_STORE.load(cls))

    _available_locales: dict[str, MExLocale] = {}
    _translations: dict[str, GNUTranslations] = {}

    def __init__(self) -> None:
        """Initialize with all available locales."""
        for mo_file in cast("Path", (files("mex.model") / "i18n")).glob("*.mo"):
            locale = mo_file.name.removesuffix(".mo")
            language = re.split("[-_]", locale)[0]
            label = BabelLocale(language).get_language_name()
            self._available_locales[locale] = MExLocale(
                id=locale, label=label, filepath=mo_file
            )

    def get_available_locales(self) -> Sequence[MExLocale]:
        """Get all available locales.

        Returns:
            All available locales.
        """
        return list(self._available_locales.values())

    def _ensure_translation(self, locale_id: str) -> GNUTranslations:
        if locale_id not in self._translations:
            with self._available_locales[locale_id].filepath.open("rb") as mo_file:
                self._translations[locale_id] = GNUTranslations(mo_file)
        return self._translations[locale_id]

    def get_field_label(  # noqa: PLR0911
        self, locale_id: str, stem_type: str, field_name: str, n: int = 1
    ) -> str:
        """Get the human readable form of the given field in a given language.

        Args:
            locale_id: The locale id of the language to use.
            stem_type: The entity type the field belongs to.
            field_name: The name of the field.
            n (optional): Number to pass to ngettext to determine if plural form is
            used. Defaults to 1.

        Returns:
            str: The human readable name of the field.
        """
        translation = self._ensure_translation(locale_id)
        msg_id_singular = f"{field_name}.singular"
        msg_id_plural = f"{field_name}.plural"

        if (
            stem_plural_singular_translation := translation.npgettext(
                stem_type, msg_id_singular, msg_id_plural, n
            )
        ) not in (msg_id_singular, msg_id_plural):
            return stem_plural_singular_translation

        if (
            plural_singular_translation := translation.ngettext(
                msg_id_singular, msg_id_plural, n
            )
        ) not in (
            msg_id_singular,
            msg_id_plural,
        ):
            return plural_singular_translation

        if (
            stem_fieldname_translation := translation.pgettext(stem_type, field_name)
        ) != field_name:
            return stem_fieldname_translation

        if (
            stem_singular_translation := translation.pgettext(
                stem_type, msg_id_singular
            )
        ) != msg_id_singular:
            return stem_singular_translation

        if (
            singular_translation := translation.gettext(msg_id_singular)
        ) != msg_id_singular:
            return singular_translation

        if (fieldname_translation := translation.gettext(field_name)) != field_name:
            return fieldname_translation

        return camelcase_to_title(field_name)

    def get_field_description(
        self, locale_id: str, stem_type: str, field_name: str
    ) -> str:
        """Get the description for a field in a given language.

        Args:
            locale_id: The locale id of the language to use.
            stem_type: The type the field belongs to.
            field_name: The name of the field.

        Returns:
            str: The description of the field.
        """
        translation = self._ensure_translation(locale_id)
        msg_id_description = f"{field_name}.description"
        if (
            description := translation.pgettext(stem_type, msg_id_description)
        ) != msg_id_description:
            return description

        if (
            description := translation.gettext(msg_id_description)
        ) != msg_id_description:
            return description

        return ""
