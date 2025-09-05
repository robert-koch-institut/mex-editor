import gettext
import re
from pathlib import Path
from typing import Self, cast

from mex.common.context import SingleSingletonStore

# TODO(FE): Change to mex-model when fork is approved
here = Path(__file__).resolve().parent

LOCALE_FOLDER_PATH = here / "../../locales"
LOCALE_DE = "de-DE"
LOCALE_EN = "en-US"
LOCALES_AVAILABLE = [LOCALE_DE, LOCALE_EN]
LOCALES_LABEL_MAPPING = {LOCALE_DE: "deutsch", LOCALE_EN: "english"}

LOCALE_SERVICE_STORE = SingleSingletonStore["LocaleService"]()


def camelcase_to_title(value: str) -> str:
    """Convert a camelcase string into titlecased words splitted by space.

    Args:
        value: The camelcase string to convert.

    Returns:
        str: The converted string containing titlecased words splitted by space.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", " ", value).title()


def get_locale_label(locale: str) -> str:
    """Convert the locale into a label.

    Args:
        locale: The locale to convert to a label.

    Returns:
        str: The label for the given locale.
    """
    return LOCALES_LABEL_MAPPING[locale]


# IDEA: Propably cleaner to split this into LocalService(str -> translation + ensure
# fallback translation if str is no valid language or doesnt exist) and
# FieldHelper(label and description for fields)
class LocaleService:
    """A service singleton to control the current locale used by the app."""

    _current_locale: str = ""
    _translation: gettext.GNUTranslations

    @classmethod
    def get(cls) -> Self:
        """Get singleton instance of the LocaleService.

        Returns:
            Self: The LocaleService singleton.
        """
        return cast("Self", LOCALE_SERVICE_STORE.load(cls))

    def __init__(self, locale: str = LOCALES_AVAILABLE[0]) -> None:
        """Init with locale to use. Use first available locale if not specified.

        Args:
            locale (str, optional): The locale to use for the app.
            Defaults to LOCALES_AVAILABLE[0].
        """
        self.set_locale(locale=locale)

    def set_locale(self, locale: str) -> None:
        """Set the locale to use within the app.

        Args:
            locale: The locale to use within the app.
        """
        if self._current_locale != locale:
            self._current_locale = locale

            mo_path = LOCALE_FOLDER_PATH / f"{locale}.mo"
            with Path.open(mo_path, "rb") as mo_file:
                self._translation = gettext.GNUTranslations(mo_file)

    def get_locale(self) -> str:
        """Get the current locale of the app.

        Returns:
            str: The current locale of the app.
        """
        return self._current_locale

    def get_field_label(self, stem_type: str, field_name: str, n: int = 1) -> str:
        """Get the human readable form the given field.

        Args:
            stem_type: The entity type the field belongs to.
            field_name: The name of the field.
            n (optional): Number to pass to ngettext to determine if plural form is
            used. Defaults to 1.

        Returns:
            str: The human readable name of the field.
        """
        translation = self._translation
        msg_id1 = f"{field_name}.singular"
        msg_id2 = f"{field_name}.plural"

        # each finder consists of a func to find a translation and a func that verifies
        # if the found translation is a real translation or just a key (which gets
        # returned if nothing is found)
        trans_finders = [
            # find plural or singular field for stem_type (most specific)
            (
                lambda: translation.npgettext(stem_type, msg_id1, msg_id2, n),
                lambda x: x not in (msg_id1, msg_id2),
            ),
            # find field for stem_type
            (
                lambda: translation.pgettext(stem_type, field_name),
                lambda x: x != field_name,
            ),
            # find plural or singular field WITHOUT stem_type
            (
                lambda: translation.ngettext(msg_id1, msg_id2, n),
                lambda x: x not in (msg_id1, msg_id2),
            ),
            # find singular field for stem_type
            (
                lambda: translation.pgettext(stem_type, msg_id1),
                lambda x: x != msg_id1,
            ),
            # find singular field WITHOUT stem_type
            (
                lambda: translation.gettext(msg_id1),
                lambda x: x != msg_id1,
            ),
            # find field WITHOUT stem_type
            (
                lambda: translation.gettext(field_name),
                lambda x: x != field_name,
            ),
        ]

        trans: str = ""
        found_trans = False
        for finder in trans_finders:
            trans = finder[0]()
            if found_trans := finder[1](trans):
                break

        return trans if found_trans else camelcase_to_title(field_name)

    def get_field_description(self, stem_type: str, field_name: str) -> str:
        """Get the description for a field.

        Args:
            stem_type: The type the field belongs to.
            field_name: The name of the field.

        Returns:
            str: The description of the field.
        """
        if not self._translation:
            return ""

        translation = self._translation
        desc_key = f"{field_name}.description"
        trans_finders = [
            # find description by field_name and stem_type
            (
                lambda: translation.pgettext(stem_type, desc_key),
                lambda x: x != desc_key,
            ),
            # find description by field_name
            (
                lambda: translation.gettext(desc_key),
                lambda x: x != desc_key,
            ),
        ]

        trans: str = ""
        found_trans = False
        for finder in trans_finders:
            trans = finder[0]()
            if found_trans := finder[1](trans):
                break

        return trans if found_trans else ""
