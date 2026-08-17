from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import json
import platform

import pytest

from src.re.adapters.excel.com_runner import WindowsExcelCOMRunner
from src.re.application.services.excel_qualification import (
    ExcelQualificationReport,
    QualificationStatus,
    REPORT_SCHEMA_VERSION,
    qualify_workbook,
)
from src.re.application.services.golden_fixture import (
    CheckpointManifest,
    CheckpointSpec,
    ComparisonKind,
    ComparisonPolicy,
)
from src.re.ports.excel_qualification import (
    ExcelCheckpointValue,
    ExcelExecutionEvidence,
    ExcelRunnerProbe,
)


DIGEST = "a" * 64


def manifest() -> CheckpointManifest:
    return CheckpointManifest(
        manifest_id="m1",
        version=1,
        fixture_id="fixture-1",
        status="TEST",
        source_contract="test",
        tolerance_contract="test",
        semantic_sha256="b" * 64,
        checkpoint_set_sha256=DIGEST,
        checkpoints=(
            CheckpointSpec("Bangtinh!F108", "x", Decimal("196308350"), ComparisonPolicy(ComparisonKind.EXACT_DECIMAL), "VND/m2"),
            CheckpointSpec("Bangtinh!G182", "y", Decimal("19581000000"), ComparisonPolicy(ComparisonKind.EXACT_INTEGER), "VND"),
        ),
        source_path="memory",
    )


class UnavailableRunner:
    ran = False
    def probe(self):
        return ExcelRunnerProbe(False, "runner", "1", "EXCEL_UNAVAILABLE", "Excel unavailable")
    def run(self, workbook_path, checkpoint_ids):
        self.ran = True
        raise AssertionError("must not run")


class FakeRunner:
    def __init__(self, evidence):
        self.evidence = evidence
    def probe(self):
        return ExcelRunnerProbe(True, "runner", "1", "EXCEL_AVAILABLE", "available", "16.0")
    def run(self, workbook_path, checkpoint_ids):
        return self.evidence


def evidence(path: Path, *, values=None, actual=True, recalc=True, links=True):
    import hashlib
    h=hashlib.sha256(path.read_bytes()).hexdigest()
    values = values or (("Bangtinh!F108","196308350"),("Bangtinh!G182","19581000000"))
    return ExcelExecutionEvidence(
        "runner","1","16.0",h,actual,recalc,links,
        tuple(ExcelCheckpointValue(k,v) for k,v in values),
    )


def test_unavailable_excel_is_not_qualified_and_does_not_run(tmp_path):
    wb=tmp_path/"book.xlsx"; wb.write_bytes(b"not-real-xlsx")
    runner=UnavailableRunner()
    report=qualify_workbook(
        workbook_path=wb, profile_id="p", profile_version="v1",
        manifest=manifest(), runner=runner,
    )
    assert report.status is QualificationStatus.NOT_QUALIFIED
    assert report.reason_code == "EXCEL_UNAVAILABLE"
    assert report.actual_excel_evidence is False
    assert all(x.passed is None for x in report.checkpoints)
    assert runner.ran is False


def test_actual_excel_all_required_checkpoints_can_pass(tmp_path):
    wb=tmp_path/"book.xlsx"; wb.write_bytes(b"x")
    report=qualify_workbook(
        workbook_path=wb, profile_id="p", profile_version="v1",
        manifest=manifest(), runner=FakeRunner(evidence(wb)),
    )
    assert report.status is QualificationStatus.PASS
    assert report.actual_excel_evidence is True
    assert report.full_recalculation_performed is True
    assert report.opened_without_link_updates is True
    assert all(x.passed is True for x in report.checkpoints)


def test_checkpoint_failure_blocks_pass(tmp_path):
    wb=tmp_path/"book.xlsx"; wb.write_bytes(b"x")
    ev=evidence(wb, values=(("Bangtinh!F108","196308350"),("Bangtinh!G182","19582000000")))
    report=qualify_workbook(
        workbook_path=wb, profile_id="p", profile_version="v1",
        manifest=manifest(), runner=FakeRunner(ev),
    )
    assert report.status is QualificationStatus.FAILED
    assert report.reason_code == "CHECKPOINT_VERIFICATION_FAILED"
    assert [x.checkpoint_id for x in report.checkpoints if x.passed is False] == ["Bangtinh!G182"]


@pytest.mark.parametrize(
    ("field","code"),
    [
        ("actual_excel_evidence","EXCEL_EVIDENCE_MISSING"),
        ("full_recalculation_performed","FULL_RECALC_NOT_EVIDENCED"),
        ("opened_without_link_updates","LINK_UPDATE_POLICY_NOT_EVIDENCED"),
    ],
)
def test_incomplete_execution_evidence_cannot_pass(tmp_path, field, code):
    wb=tmp_path/"book.xlsx"; wb.write_bytes(b"x")
    ev=evidence(wb)
    ev=replace(ev, **{field:False})
    report=qualify_workbook(
        workbook_path=wb, profile_id="p", profile_version="v1",
        manifest=manifest(), runner=FakeRunner(ev),
    )
    assert report.status is QualificationStatus.NOT_QUALIFIED
    assert report.reason_code == code


def test_workbook_hash_mismatch_is_not_qualified(tmp_path):
    wb=tmp_path/"book.xlsx"; wb.write_bytes(b"x")
    ev=replace(evidence(wb), workbook_sha256="b"*64)
    report=qualify_workbook(
        workbook_path=wb, profile_id="p", profile_version="v1",
        manifest=manifest(), runner=FakeRunner(ev),
    )
    assert report.status is QualificationStatus.NOT_QUALIFIED
    assert report.reason_code == "WORKBOOK_HASH_MISMATCH"


def test_report_constructor_rejects_pass_without_real_excel_evidence():
    with pytest.raises(ValueError, match="actual Excel evidence"):
        ExcelQualificationReport(
            REPORT_SCHEMA_VERSION, QualificationStatus.PASS, "QUALIFIED", "x",
            "p","v1",DIGEST,"m1",1,DIGEST,"runner","1","16.0",
            False,True,True,(),
        )


def test_report_json_is_deterministic_and_contains_required_binding_fields(tmp_path):
    wb=tmp_path/"book.xlsx"; wb.write_bytes(b"x")
    report=qualify_workbook(
        workbook_path=wb, profile_id="profile-1", profile_version="7",
        manifest=manifest(), runner=UnavailableRunner(),
    )
    a=report.to_json(); b=report.to_json()
    assert a == b
    payload=json.loads(a)
    assert payload["schema_version"] == 1
    assert payload["profile_id"] == "profile-1"
    assert payload["profile_version"] == "7"
    assert payload["workbook_sha256"]
    assert payload["manifest_id"] == "m1"
    assert payload["manifest_version"] == 1
    assert payload["checkpoint_set_sha256"] == DIGEST
    assert [x["checkpoint_id"] for x in payload["checkpoints"]] == ["Bangtinh!F108","Bangtinh!G182"]


def test_non_windows_probe_is_not_qualified(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    probe=WindowsExcelCOMRunner().probe()
    assert probe.available is False
    assert probe.reason_code == "UNSUPPORTED_PLATFORM"


class FakeRange:
    def __init__(self, value): self.Value2=value
class FakeSheet:
    def __init__(self, values): self.values=values
    def Range(self, cell): return FakeRange(self.values[cell])
class FakeSheets:
    def __init__(self, values): self.values=values
    def __call__(self, sheet): return FakeSheet(self.values[sheet])
class FakeWorkbook:
    def __init__(self):
        self.Worksheets=FakeSheets({"Bangtinh":{"F108":196308350.0,"G182":19581000000.0}})
        self.closed=None
    def Close(self, SaveChanges=False): self.closed=SaveChanges
class FakeWorkbooks:
    def __init__(self, wb): self.wb=wb; self.open_kwargs=None
    def Open(self, path, **kwargs): self.open_kwargs=kwargs; return self.wb
class FakeExcel:
    def __init__(self):
        self.Version="16.0"; self.CalculationState=0; self.calc=False; self.quit=False
        self.wb=FakeWorkbook(); self.Workbooks=FakeWorkbooks(self.wb)
    def CalculateFullRebuild(self): self.calc=True
    def Quit(self): self.quit=True


def test_com_runner_interface_opens_without_links_and_full_recalculates(tmp_path):
    wb_path=tmp_path/"book.xlsx"; wb_path.write_bytes(b"xlsx-bytes")
    excel=FakeExcel()
    runner=WindowsExcelCOMRunner(dispatch_factory=lambda _:excel)
    ev=runner.run(str(wb_path), ("Bangtinh!F108","Bangtinh!G182"))
    assert excel.Workbooks.open_kwargs["UpdateLinks"] == 0
    assert excel.Workbooks.open_kwargs["ReadOnly"] is True
    assert excel.calc is True
    assert excel.wb.closed is False
    assert excel.quit is True
    assert ev.actual_excel_evidence is True
    assert ev.full_recalculation_performed is True
    assert ev.opened_without_link_updates is True
    assert dict((x.checkpoint_id,x.value) for x in ev.checkpoint_values) == {
        "Bangtinh!F108":"196308350.0",
        "Bangtinh!G182":"19581000000.0",
    }
