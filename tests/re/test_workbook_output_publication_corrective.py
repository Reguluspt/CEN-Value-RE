from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from threading import Barrier

import pytest
from openpyxl import Workbook
from openpyxl.workbook.workbook import Workbook as OpenPyxlWorkbook

import src.re.adapters.excel_output.openpyxl_writer as writer_module
from src.re.adapters.excel_output.n08_0038 import N08_0038_OUTPUT_PROFILE
from src.re.adapters.excel_output.openpyxl_writer import (
    OpenPyxlWorkbookOutputWriter,
    WorkbookWriteContractError,
)
from src.re.adapters.excel_output.profile import WorkbookValueKind
from src.re.ports.workbook_output import WorkbookGenerationSourceBinding


def _file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _synthetic_n08(path: Path) -> None:
    workbook = Workbook()
    workbook.remove(workbook.active)
    for requirement in N08_0038_OUTPUT_PROFILE.template_profile.required_sheets:
        worksheet = workbook.create_sheet(requirement.name)
        worksheet.sheet_state = requirement.state.value
    for signature in N08_0038_OUTPUT_PROFILE.template_profile.formula_signatures:
        sheet, coordinate = signature.cell.rsplit("!", 1)
        workbook[sheet][coordinate] = signature.formula
    workbook["Phieu TTTT"]["E5"] = "='[1]Nhập liệu'!F9"
    workbook["Phieu TTTT"]["B18"] = "=ROUND(B15*B19,-7)"
    workbook["Sheet1"]["Z99"] = "UNKNOWN-SENTINEL"
    workbook.save(path)
    workbook.close()


def _writer_for_source(source: Path):
    profile = replace(
        N08_0038_OUTPUT_PROFILE,
        source_exemplar_sha256=_file_sha(source),
        fixed_source_bindings=(),
    )
    return OpenPyxlWorkbookOutputWriter((profile,)), profile


def _values(profile):
    values = {}
    for binding in (*profile.write_bindings, *profile.compatibility_bindings):
        if binding.value_kind is WorkbookValueKind.TEXT:
            values[binding.source_key] = (
                "Tp. HCM" if binding.source_key == "subject.province" else "TEXT"
            )
        elif binding.value_kind is WorkbookValueKind.FRACTION:
            values[binding.source_key] = "0.05"
        else:
            values[binding.source_key] = "123.45"
    return values


def _binding():
    return WorkbookGenerationSourceBinding(
        case_id="case-1",
        final_valuation_snapshot_id="final-1",
        final_valuation_semantic_sha256="a" * 64,
    )


def _generate(writer, profile, source: Path, output: Path):
    return writer.generate(
        profile_id=profile.profile_id,
        profile_version=profile.profile_version,
        template_path=str(source),
        output_path=str(output),
        values=_values(profile),
        source_binding=_binding(),
        generated_at="2026-08-18T08:00:00Z",
    )


def _owned_temps(directory: Path, output: Path):
    return tuple(directory.glob(f".{output.stem}.*.tmp.xlsx*"))


def test_destination_created_after_validation_is_not_overwritten_or_deleted(
    tmp_path, monkeypatch
):
    source = tmp_path / "source.xlsx"
    output = tmp_path / "generated.xlsx"
    sentinel = b"FOREIGN-DESTINATION-SENTINEL"
    _synthetic_n08(source)
    writer, profile = _writer_for_source(source)
    real_link = writer_module.os.link

    def racing_link(src, dst):
        Path(dst).write_bytes(sentinel)
        return real_link(src, dst)

    monkeypatch.setattr(writer_module.os, "link", racing_link)

    with pytest.raises(WorkbookWriteContractError, match="became occupied"):
        _generate(writer, profile, source, output)

    assert output.read_bytes() == sentinel
    assert _owned_temps(tmp_path, output) == ()


def test_two_competing_attempts_have_at_most_one_success(tmp_path, monkeypatch):
    source = tmp_path / "source.xlsx"
    output = tmp_path / "generated.xlsx"
    _synthetic_n08(source)
    writer_a, profile = _writer_for_source(source)
    writer_b = OpenPyxlWorkbookOutputWriter((profile,))
    real_link = writer_module.os.link
    barrier = Barrier(2)

    def synchronized_link(src, dst):
        barrier.wait(timeout=15)
        return real_link(src, dst)

    monkeypatch.setattr(writer_module.os, "link", synchronized_link)

    def attempt(writer):
        try:
            return "SUCCESS", _generate(writer, profile, source, output)
        except WorkbookWriteContractError as exc:
            return "REJECTED", exc

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(executor.map(attempt, (writer_a, writer_b)))

    assert sorted(item[0] for item in results) == ["REJECTED", "SUCCESS"]
    artifact = next(item[1] for item in results if item[0] == "SUCCESS")
    assert output.exists()
    assert _file_sha(output) == artifact.output_sha256
    assert _owned_temps(tmp_path, output) == ()


def test_save_failure_cleans_owned_temp_without_deleting_foreign_destination(
    tmp_path, monkeypatch
):
    source = tmp_path / "source.xlsx"
    output = tmp_path / "generated.xlsx"
    sentinel = b"FOREIGN-FILE-CREATED-DURING-SAVE"
    _synthetic_n08(source)
    writer, profile = _writer_for_source(source)
    real_save = OpenPyxlWorkbook.save

    def injected_save(self, filename):
        target = Path(filename)
        if target.name.startswith(f".{output.stem}.") and target.name.endswith(
            ".tmp.xlsx"
        ):
            target.write_bytes(b"PARTIAL-OWNED-TEMP")
            output.write_bytes(sentinel)
            raise OSError("injected workbook.save failure")
        return real_save(self, filename)

    monkeypatch.setattr(OpenPyxlWorkbook, "save", injected_save)

    with pytest.raises(OSError, match="injected workbook.save failure"):
        _generate(writer, profile, source, output)

    assert output.read_bytes() == sentinel
    assert _owned_temps(tmp_path, output) == ()
