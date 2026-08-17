"""Trusted template rounding-default resolution for application consumers."""

from __future__ import annotations

from ...ports.excel import TemplateRoundingDefaultRecord
from .n08_0038 import N08_0038_PROFILE
from .profile import ExcelTemplateProfile


class ExcelTemplateRoundingDefaultResolver:
    """Resolve defaults only from frozen supported ExcelTemplateProfile objects."""

    def __init__(self, profiles: tuple[ExcelTemplateProfile, ...]) -> None:
        self._profiles = profiles

    def resolve(
        self,
        *,
        profile_id: str,
        profile_version: str,
        target: str,
    ) -> TemplateRoundingDefaultRecord | None:
        for profile in self._profiles:
            if (
                profile.profile_id != profile_id
                or profile.profile_version != profile_version
            ):
                continue
            default = profile.rounding_default_for(target)
            if default is None:
                return None
            return TemplateRoundingDefaultRecord(
                profile_id=profile.profile_id,
                profile_version=profile.profile_version,
                target=default.target,
                mode=default.mode,
                increment_vnd=default.increment_vnd,
            )
        return None


SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS = ExcelTemplateRoundingDefaultResolver(
    (N08_0038_PROFILE,)
)
