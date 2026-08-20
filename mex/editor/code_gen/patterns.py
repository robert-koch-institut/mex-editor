"""Written by Claude (Anthropic).

Assigns each distinct regex pattern encountered across all bundles a
single, meaningful, reusable TypeScript constant name (deduplicated by
pattern content, not by field)."""
from __future__ import annotations
import re

# mex-common's Merged*Identifier types all share this exact regex.
IDENTIFIER_PATTERN = r"^[a-zA-Z0-9]{14,22}$"

# Recognizable-by-class-name patterns get a friendly stem instead of one
# derived mechanically from the class name.
_KNOWN = {"YearMonthDayTime": "yearMonthDayTime", "YearMonthDay": "yearMonthDay", "YearMonth": "yearMonth", "Year": "year"}
# Leaf classes too generic to name a pattern after -- fall back to the
# field name instead (e.g. "email" -> emailPattern).
_GENERIC = {"str", "int", "float", "bool"}


def _name(hint: str) -> str:
    # Strip anything that can't appear in a TS identifier, then camelCase.
    c = re.sub(r"[^A-Za-z0-9]", "", hint) or "value"
    return c[0].lower() + c[1:] + "Pattern"


class PatternRegistry:
    """Call `name_for()` for every pattern a generator emits; identical
    patterns get the same name, and name collisions between two genuinely
    different patterns are auto-disambiguated."""

    def __init__(self) -> None:
        self._by_pattern: dict[str, str] = {}
        self._by_name: dict[str, str] = {}

    def name_for(self, pattern: str, leaf_cls_name: str, field_name: str | None = None) -> str:
        """Return `pattern`'s constant name, registering it on first use."""
        if pattern in self._by_pattern:
            return self._by_pattern[pattern]
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
