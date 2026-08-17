"""Framework-independent Excel qualification runner contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ExcelRunnerProbe:
    available: bool
    runner_id: str
    runner_version: str
    reason_code: str
    reason: str
    excel_version: str | None = None

    def __post_init__(self) -> None:
        if not self.runner_id.strip() or not self.runner_version.strip():
            raise ValueError("runner identity/version required")
        if not self.reason_code.strip() or not self.reason.strip():
            raise ValueError("probe reason code/message required")
        if self.available and not (self.excel_version and self.excel_version.strip()):
            raise ValueError("available Excel probe requires excel_version")


@dataclass(frozen=True, slots=True)
class ExcelCheckpointValue:
    checkpoint_id: str
    value: str

    def __post_init__(self) -> None:
        if not self.checkpoint_id.strip():
            raise ValueError("checkpoint_id required")


@dataclass(frozen=True, slots=True)
class ExcelExecutionEvidence:
    runner_id: str
    runner_version: str
    excel_version: str
    workbook_sha256: str
    actual_excel_evidence: bool
    full_recalculation_performed: bool
    opened_without_link_updates: bool
    checkpoint_values: tuple[ExcelCheckpointValue, ...]

    def __post_init__(self) -> None:
        if not self.runner_id.strip() or not self.runner_version.strip():
            raise ValueError("runner identity/version required")
        if not self.excel_version.strip():
            raise ValueError("Excel execution evidence requires excel_version")
        if len(self.workbook_sha256) != 64 or any(
            ch not in "0123456789abcdef" for ch in self.workbook_sha256
        ):
            raise ValueError("workbook_sha256 must be lowercase SHA-256")
        ids = [row.checkpoint_id for row in self.checkpoint_values]
        if len(ids) != len(set(ids)):
            raise ValueError("checkpoint evidence IDs must be unique")


class ExcelQualificationRunner(Protocol):
    def probe(self) -> ExcelRunnerProbe:
        """Return runner/Excel availability without qualifying a workbook."""

    def run(
        self,
        workbook_path: str,
        checkpoint_ids: tuple[str, ...],
    ) -> ExcelExecutionEvidence:
        """Execute real Excel qualification and return runtime evidence."""
