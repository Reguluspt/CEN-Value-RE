"""Excel compatibility port boundary.

No openpyxl/COM dependency is permitted in this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class TemplateRoundingDefaultRecord:
    """Trusted effective rounding metadata supplied by a template-profile adapter."""

    profile_id: str
    profile_version: str
    target: str
    mode: str
    increment_vnd: int | None


class TemplateRoundingDefaultResolver(Protocol):
    """Resolve a frozen template rounding default without exposing adapter types."""

    def resolve(
        self,
        *,
        profile_id: str,
        profile_version: str,
        target: str,
    ) -> TemplateRoundingDefaultRecord | None: ...
