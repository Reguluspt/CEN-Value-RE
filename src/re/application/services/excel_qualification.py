"""Excel qualification orchestration.

This service never automates Excel directly. It consumes a runner port and
the versioned Golden Fixture checkpoint manifest. PASS is fail-closed: actual
Excel execution, full recalculation, no-link-update opening and every required
checkpoint must all be evidenced.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from src.re.application.services.golden_fixture import (
    CheckpointManifest,
    evaluate_checkpoint_results,
)
from src.re.ports.excel_qualification import (
    ExcelExecutionEvidence,
    ExcelQualificationRunner,
)


REPORT_SCHEMA_VERSION = 1


class QualificationStatus(str, Enum):
    PASS = "PASS"
    FAILED = "FAILED"
    NOT_QUALIFIED = "NOT_QUALIFIED"


@dataclass(frozen=True, slots=True)
class QualificationCheckpoint:
    checkpoint_id: str
    passed: bool | None
    expected: str
    actual: str | None
    reason: str


@dataclass(frozen=True, slots=True)
class ExcelQualificationReport:
    schema_version: int
    status: QualificationStatus
    reason_code: str
    reason: str
    profile_id: str
    profile_version: str
    workbook_sha256: str
    manifest_id: str
    manifest_version: int
    checkpoint_set_sha256: str
    runner_id: str
    runner_version: str
    excel_version: str | None
    actual_excel_evidence: bool
    full_recalculation_performed: bool
    opened_without_link_updates: bool
    checkpoints: tuple[QualificationCheckpoint, ...]

    def __post_init__(self) -> None:
        if self.schema_version != REPORT_SCHEMA_VERSION:
            raise ValueError("unsupported qualification report schema_version")
        for field_name, value in (
            ("reason_code", self.reason_code),
            ("reason", self.reason),
            ("profile_id", self.profile_id),
            ("profile_version", self.profile_version),
            ("manifest_id", self.manifest_id),
            ("runner_id", self.runner_id),
            ("runner_version", self.runner_version),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} must not be blank")
        if self.manifest_version < 1:
            raise ValueError("manifest_version must be positive")
        for digest_name, value in (
            ("workbook_sha256", self.workbook_sha256),
            ("checkpoint_set_sha256", self.checkpoint_set_sha256),
        ):
            if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                raise ValueError(f"{digest_name} must be lowercase SHA-256")
        ids = [row.checkpoint_id for row in self.checkpoints]
        if len(ids) != len(set(ids)):
            raise ValueError("qualification checkpoint IDs must be unique")

        if self.status is QualificationStatus.PASS:
            if not self.actual_excel_evidence:
                raise ValueError("PASS requires actual Excel evidence")
            if not self.full_recalculation_performed:
                raise ValueError("PASS requires full Excel recalculation evidence")
            if not self.opened_without_link_updates:
                raise ValueError("PASS requires no-link-update open evidence")
            if not (self.excel_version and self.excel_version.strip()):
                raise ValueError("PASS requires Excel version evidence")
            if not self.checkpoints or any(row.passed is not True for row in self.checkpoints):
                raise ValueError("PASS requires every checkpoint to pass")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )


def workbook_sha256(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _not_run_checkpoints(
    manifest: CheckpointManifest,
    reason: str,
) -> tuple[QualificationCheckpoint, ...]:
    return tuple(
        QualificationCheckpoint(
            checkpoint_id=spec.checkpoint_id,
            passed=None,
            expected=str(spec.expected),
            actual=None,
            reason=reason,
        )
        for spec in manifest.checkpoints
    )


def _base_report(
    *,
    status: QualificationStatus,
    reason_code: str,
    reason: str,
    profile_id: str,
    profile_version: str,
    workbook_hash: str,
    manifest: CheckpointManifest,
    runner_id: str,
    runner_version: str,
    excel_version: str | None,
    actual_excel_evidence: bool,
    full_recalculation_performed: bool,
    opened_without_link_updates: bool,
    checkpoints: tuple[QualificationCheckpoint, ...],
) -> ExcelQualificationReport:
    return ExcelQualificationReport(
        schema_version=REPORT_SCHEMA_VERSION,
        status=status,
        reason_code=reason_code,
        reason=reason,
        profile_id=profile_id,
        profile_version=profile_version,
        workbook_sha256=workbook_hash,
        manifest_id=manifest.manifest_id,
        manifest_version=manifest.version,
        checkpoint_set_sha256=manifest.checkpoint_set_sha256,
        runner_id=runner_id,
        runner_version=runner_version,
        excel_version=excel_version,
        actual_excel_evidence=actual_excel_evidence,
        full_recalculation_performed=full_recalculation_performed,
        opened_without_link_updates=opened_without_link_updates,
        checkpoints=checkpoints,
    )


def qualify_workbook(
    *,
    workbook_path: str | Path,
    profile_id: str,
    profile_version: str,
    manifest: CheckpointManifest,
    runner: ExcelQualificationRunner,
) -> ExcelQualificationReport:
    path = Path(workbook_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if not profile_id.strip() or not profile_version.strip():
        raise ValueError("profile identity/version required")

    workbook_hash = workbook_sha256(path)
    probe = runner.probe()
    if not probe.available:
        return _base_report(
            status=QualificationStatus.NOT_QUALIFIED,
            reason_code=probe.reason_code,
            reason=probe.reason,
            profile_id=profile_id,
            profile_version=profile_version,
            workbook_hash=workbook_hash,
            manifest=manifest,
            runner_id=probe.runner_id,
            runner_version=probe.runner_version,
            excel_version=probe.excel_version,
            actual_excel_evidence=False,
            full_recalculation_performed=False,
            opened_without_link_updates=False,
            checkpoints=_not_run_checkpoints(manifest, "Excel qualification not run"),
        )

    try:
        evidence = runner.run(str(path), manifest.checkpoint_ids)
    except Exception as exc:
        return _base_report(
            status=QualificationStatus.NOT_QUALIFIED,
            reason_code="EXCEL_RUNNER_EXECUTION_UNAVAILABLE",
            reason=f"Excel runner did not produce qualification evidence: {type(exc).__name__}",
            profile_id=profile_id,
            profile_version=profile_version,
            workbook_hash=workbook_hash,
            manifest=manifest,
            runner_id=probe.runner_id,
            runner_version=probe.runner_version,
            excel_version=probe.excel_version,
            actual_excel_evidence=False,
            full_recalculation_performed=False,
            opened_without_link_updates=False,
            checkpoints=_not_run_checkpoints(manifest, "Excel qualification not completed"),
        )

    gate = _validate_execution_evidence(evidence, workbook_hash)
    if gate is not None:
        code, reason = gate
        return _base_report(
            status=QualificationStatus.NOT_QUALIFIED,
            reason_code=code,
            reason=reason,
            profile_id=profile_id,
            profile_version=profile_version,
            workbook_hash=workbook_hash,
            manifest=manifest,
            runner_id=evidence.runner_id,
            runner_version=evidence.runner_version,
            excel_version=evidence.excel_version,
            actual_excel_evidence=evidence.actual_excel_evidence,
            full_recalculation_performed=evidence.full_recalculation_performed,
            opened_without_link_updates=evidence.opened_without_link_updates,
            checkpoints=_not_run_checkpoints(manifest, "Execution evidence incomplete"),
        )

    actual = {row.checkpoint_id: row.value for row in evidence.checkpoint_values}
    checkpoint_report = evaluate_checkpoint_results(manifest, actual, strict_checkpoint_set=True)
    rows = tuple(
        QualificationCheckpoint(
            checkpoint_id=outcome.checkpoint_id,
            passed=outcome.passed,
            expected=str(outcome.expected),
            actual=None if outcome.actual is None else str(outcome.actual),
            reason=outcome.reason,
        )
        for outcome in checkpoint_report.outcomes
    )
    status = QualificationStatus.PASS if checkpoint_report.passed else QualificationStatus.FAILED
    reason_code = "QUALIFIED" if checkpoint_report.passed else "CHECKPOINT_VERIFICATION_FAILED"
    reason = (
        "Actual Excel full-recalculation evidence and all required checkpoints passed"
        if checkpoint_report.passed
        else "Actual Excel evidence exists but required checkpoint verification failed"
    )
    return _base_report(
        status=status,
        reason_code=reason_code,
        reason=reason,
        profile_id=profile_id,
        profile_version=profile_version,
        workbook_hash=workbook_hash,
        manifest=manifest,
        runner_id=evidence.runner_id,
        runner_version=evidence.runner_version,
        excel_version=evidence.excel_version,
        actual_excel_evidence=evidence.actual_excel_evidence,
        full_recalculation_performed=evidence.full_recalculation_performed,
        opened_without_link_updates=evidence.opened_without_link_updates,
        checkpoints=rows,
    )


def _validate_execution_evidence(
    evidence: ExcelExecutionEvidence,
    expected_workbook_hash: str,
) -> tuple[str, str] | None:
    if evidence.workbook_sha256 != expected_workbook_hash:
        return (
            "WORKBOOK_HASH_MISMATCH",
            "Excel evidence is bound to a different workbook hash",
        )
    if not evidence.actual_excel_evidence:
        return ("EXCEL_EVIDENCE_MISSING", "Runner did not attest actual Excel automation")
    if not evidence.full_recalculation_performed:
        return ("FULL_RECALC_NOT_EVIDENCED", "Full Excel recalculation was not evidenced")
    if not evidence.opened_without_link_updates:
        return (
            "LINK_UPDATE_POLICY_NOT_EVIDENCED",
            "Workbook open-without-arbitrary-link-updates was not evidenced",
        )
    return None


def write_qualification_report(report: ExcelQualificationReport, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report.to_json() + "\n", encoding="utf-8")
