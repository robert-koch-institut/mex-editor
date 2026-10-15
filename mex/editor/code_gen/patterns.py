import re

from mex.common.types import IDENTIFIER_PATTERN

# Recognizable-by-class-name patterns get a friendly stem instead of one
# derived mechanically from the class name.
_KNOWN = {
    "YearMonthDayTime": "yearMonthDayTime",
    "YearMonthDay": "yearMonthDay",
    "YearMonth": "yearMonth",
    "Year": "year",
}
# Leaf classes too generic to name a pattern after -- fall back to the
# field name instead (e.g. "email" -> emailPattern).
_GENERIC = {"str", "int", "float", "bool"}


# Constructs Python's `re` accepts but JavaScript's RegExp does not. A
# generated `new RegExp(...)` carrying one of these throws at module load,
# which takes down the whole bundle -- so refuse to emit it at all.
_JS_INCOMPATIBLE = [
    (r"\(\?P<", "named group `(?P<name>...)` -- JavaScript spells it `(?<name>...)`"),
    (r"\(\?P=", "named backreference `(?P=name)` -- JavaScript spells it `\\k<name>`"),
    (r"\(\?#", "inline comment `(?#...)`"),
    (r"\(\?[aiLmsux]+[):]", "inline flag group like `(?i)` or `(?i:...)`"),
    (r"[*+?}][+]", "possessive quantifier like `a*+`"),
    (r"\(\?>", "atomic group `(?>...)`"),
    (r"\\A", "the `\\A` anchor -- JavaScript spells it `^`"),
    (r"\\Z", "the `\\Z` anchor -- JavaScript spells it `$`"),
    (r"\\z", "the `\\z` anchor -- JavaScript spells it `$`"),
]


def js_incompatibility(pattern: str) -> str | None:
    r"""Name the first JavaScript-incompatible construct in `pattern`, if any.

    Best-effort and deliberately conservative: escaped backslashes are blanked
    out first so a literal `\\A` isn't mistaken for the `\A` anchor, but this
    does not otherwise parse the regex.
    """
    scrubbed = pattern.replace("\\\\", "\x00\x00")
    for probe, explanation in _JS_INCOMPATIBLE:
        if re.search(probe, scrubbed):
            return explanation
    return None


def _name(hint: str) -> str:
    """Build a TypeScript constant name from `hint`.

    Strips anything that cannot appear in a TS identifier, then camelCases.
    """
    c = re.sub(r"[^A-Za-z0-9]", "", hint) or "value"
    if c[0].isdigit():  # a TS identifier may not start with a digit
        c = f"value{c}"
    return c[0].lower() + c[1:] + "Pattern"


class PatternRegistry:
    """Assigns a stable TypeScript constant name to every distinct pattern.

    Call `name_for()` for every pattern a generator emits, across every bundle.
    Deduplication is by pattern *content*, not by field: identical patterns get
    the same name however many fields use them, and name collisions between two
    genuinely different patterns are auto-disambiguated.
    """

    def __init__(self) -> None:
        """Start out with an empty pattern registry."""
        self._by_pattern: dict[str, str] = {}
        self._by_name: dict[str, str] = {}

    def name_for(
        self, pattern: str, leaf_cls_name: str, field_name: str | None = None
    ) -> str:
        """Return `pattern`'s constant name, registering it on first use.

        Raises:
            ValueError: if `pattern` uses a construct JavaScript cannot parse.
        """
        if (problem := js_incompatibility(pattern)) is not None:
            source = f"{leaf_cls_name}.{field_name}" if field_name else leaf_cls_name
            msg = (
                f"Pattern for {source} cannot be compiled by JavaScript: it uses "
                f"{problem}. Pattern: {pattern!r}"
            )
            raise ValueError(msg)
        if pattern in self._by_pattern:
            return self._by_pattern[pattern]
        # mex-common's Merged*Identifier types all share this one regex.
        if pattern == IDENTIFIER_PATTERN:
            name = "identifierPattern"
        elif leaf_cls_name in _KNOWN:
            name = f"{_KNOWN[leaf_cls_name]}Pattern"
        elif leaf_cls_name not in _GENERIC:
            name = _name(leaf_cls_name)
        elif field_name:
            name = _name(field_name)
        else:
            name = _name(leaf_cls_name)
        base, n = name, 2
        while name in self._by_name:  # two different patterns wanting the same name
            name = f"{base}{n}"
            n += 1
        self._by_pattern[pattern] = name
        self._by_name[name] = pattern
        return name

    def all_patterns(self) -> dict[str, str]:
        """Every pattern registered so far, mapped to its constant name."""
        return dict(self._by_pattern)
