import gettext
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Self, TypedDict, cast

from mex.common.context import SingleSingletonStore

# TODO(FE): Change to mex-model when fork is approved
here = Path(__file__).resolve().parent


# class MexLocale(StrEnum):
#     """Allowed locales for MeX."""

#     DE = "de-DE"
#     EN = "en-US"


class MexLocale(TypedDict):
    filepath: str
    id: str
    label: str


LOCALE_FOLDER_PATH = here / "../../locales"
LOCALES_LABEL_MAPPING = {"de-DE": "deutsch", "en-US": "english"}
LOCALE_SERVICE_STORE = SingleSingletonStore["LocaleService"]()


def camelcase_to_title(value: str) -> str:
    """Convert a camelcase string into titlecased words splitted by space.

    Args:
        value: The camelcase string to convert.

    Returns:
        str: The converted string containing titlecased words splitted by space.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", " ", value).title()


def get_locale_label(locale_id: str) -> str:
    """Convert the locale into a label.

    Args:
        locale: The locale to convert to a label.

    Returns:
        str: The label for the given locale.
    """
    print("LABEL FOR ", locale_id)
    return LOCALES_LABEL_MAPPING[locale_id]


# IDEA: Propably cleaner to split this into LocalService(str -> translation + ensure
# fallback translation if str is no valid language or doesnt exist) and
# FieldHelper(label and description for fields)
class LocaleService:
    """A service singleton to control the current locale used by the app."""

    @classmethod
    def get(cls) -> Self:
        """Get singleton instance of the LocaleService.

        Returns:
            Self: The LocaleService singleton.
        """
        return cast("Self", LOCALE_SERVICE_STORE.load(cls))

    @classmethod
    def __init__(self) -> None:
        """Init with locale to use. Use first available locale if not specified.

        Args:
            locale (str, optional): The locale to use for the app.
            Defaults to LOCALES_AVAILABLE[0].
        """
        files = list(LOCALE_FOLDER_PATH.glob("*.mo"))
        print("FOUND FILES", files)
        self._available_locales = {
            mo_file.stem: MexLocale(
                id=mo_file.stem,
                filepath=str(mo_file),
                label=LOCALES_LABEL_MAPPING[mo_file.stem],
            )
            for mo_file in files
        }

    _available_locales: dict[str, MexLocale] = {}
    _translations: dict[str, gettext.GNUTranslations] = {}

    def get_available_locales(self) -> Sequence[MexLocale]:
        return list(self._available_locales.values())

    def _ensure_translation(self, locale_id: str):
        print("LocaleService::_ensure_translation", locale_id)
        if locale_id not in self._translations:
            with Path(self._available_locales[locale_id]["filepath"]).open(
                "rb"
            ) as mo_file:
                self._translations[locale_id] = gettext.GNUTranslations(mo_file)
        return self._translations[locale_id]

    def get_field_label(
        self, locale_id: str, stem_type: str, field_name: str, n: int = 1
    ) -> str:
        """Get the human readable form the given field.

        Args:
            stem_type: The entity type the field belongs to.
            field_name: The name of the field.
            n (optional): Number to pass to ngettext to determine if plural form is
            used. Defaults to 1.

        Returns:
            str: The human readable name of the field.
        """
        print("LocaleService::get_field_label", locale_id, stem_type, field_name, n)
        translation = self._ensure_translation(locale_id)
        msg_id1 = f"{field_name}.singular"
        msg_id2 = f"{field_name}.plural"

        # find plural or singular field for stem_type (most specific)
        if (
            translated_fieldname := translation.npgettext(
                stem_type, msg_id1, msg_id2, n
            )
        ) not in (msg_id1, msg_id2):
            return translated_fieldname

        # find plural or singular field WITHOUT stem_type
        if (translated_fieldname := translation.ngettext(msg_id1, msg_id2, n)) not in (
            msg_id1,
            msg_id2,
        ):
            return translated_fieldname

        # find field for stem_type
        if (
            translated_fieldname := translation.pgettext(stem_type, field_name)
        ) != field_name:
            return translated_fieldname

        # find singular field for stem_type
        if (
            translated_fieldname := translation.pgettext(stem_type, msg_id1)
        ) != msg_id1:
            return translated_fieldname

        # find singular field WITHOUT stem_type
        if (translated_fieldname := translation.gettext(msg_id1)) != msg_id1:
            return translated_fieldname

        # find field WITHOUT stem_type
        if (translated_fieldname := translation.gettext(field_name)) != field_name:
            return translated_fieldname

        return camelcase_to_title(field_name)

    def get_field_description(
        self, locale_id: str, stem_type: str, field_name: str
    ) -> str:
        """Get the description for a field.

        Args:
            stem_type: The type the field belongs to.
            field_name: The name of the field.

        Returns:
            str: The description of the field.
        """
        print("LocaleService::get_field_description", locale_id, stem_type, field_name)
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
