"""Regex pattern -> unique, meaningful TS constant name."""
from __future__ import annotations
import re

IDENTIFIER_PATTERN = r"^[a-zA-Z0-9]{14,22}$"
_KNOWN = {"YearMonthDayTime": "yearMonthDayTime", "YearMonthDay": "yearMonthDay", "YearMonth": "yearMonth", "Year": "year"}
_GENERIC = {"str", "int", "float", "bool"}


def _name(hint: str) -> str:
    c = re.sub(r"[^A-Za-z0-9]", "", hint) or "value"
    return c[0].lower() + c[1:] + "Pattern"


class PatternRegistry:
    def __init__(self) -> None:
        self._by_pattern: dict[str, str] = {}
        self._by_name: dict[str, str] = {}

    def name_for(self, pattern: str, leaf_cls_name: str, field_name: str | None = None) -> str:
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
        while name in self._by_name:
            name = f"{base}{n}"
            n += 1
        self._by_pattern[pattern] = name
        self._by_name[name] = pattern
        return name

    def all_patterns(self) -> dict[str, str]:
        return dict(self._by_pattern)
