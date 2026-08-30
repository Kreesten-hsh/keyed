from __future__ import annotations

from collections.abc import Iterable


def has_required_scopes(granted: Iterable[str], required: Iterable[str]) -> bool:
    return set(required).issubset(granted)
