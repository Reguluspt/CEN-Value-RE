"""Framework-independent workbook-output boundary for E1-PR-005."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

WorkbookScalar = str | int | bool | None


@dataclass(frozen=True, slots=True)
class WorkbookGenerationSourceBinding:
    case_id: str
    final_valuation_snapshot_id: str
    final_valuation_semantic_sha256: str


@dataclass(frozen=True, slots=True)
class WorkbookGenerationArtifact:
    profile_id: str
    profile_version: str
    template_path: str
    output_path: str
    source_sha256: str
    output_sha256: str
    source_binding: WorkbookGenerationSourceBinding
    generated_at: str
    changed_cells: tuple[str, ...]
    applied_transformations: tuple[str, ...]
    workbook_generated: bool = True
    excel_qualification_status: str = "NOT_RUN"

    def __post_init__(self) -> None:
        for name, value in (
            ("source_sha256", self.source_sha256),
            ("output_sha256", self.output_sha256),
            (
                "final_valuation_semantic_sha256",
                self.source_binding.final_valuation_semantic_sha256,
            ),
        ):
            if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                raise ValueError(f"{name} must be lowercase SHA-256 hex")
        if self.excel_qualification_status == "PASS":
            raise ValueError("workbook generation may not claim Excel qualification PASS")


class WorkbookOutputWriter(Protocol):
    """Generate a copy-on-write supported-profile workbook artifact."""

    def generate(
        self,
        *,
        profile_id: str,
        profile_version: str,
        template_path: str,
        output_path: str,
        values: Mapping[str, WorkbookScalar],
        source_binding: WorkbookGenerationSourceBinding,
        generated_at: str,
    ) -> WorkbookGenerationArtifact: ...
