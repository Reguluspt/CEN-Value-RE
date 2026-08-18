"""Regression proof for deterministic E1-PR-005 package metadata."""

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from time import sleep

from openpyxl import Workbook

from src.re.adapters.excel_output.n08_0038 import N08_0038_OUTPUT_PROFILE
from src.re.adapters.excel_output.openpyxl_writer import OpenPyxlWorkbookOutputWriter
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


def _binding() -> WorkbookGenerationSourceBinding:
    return WorkbookGenerationSourceBinding(
        case_id="case-1",
        final_valuation_snapshot_id="final-1",
        final_valuation_semantic_sha256="a" * 64,
    )


def test_generated_package_sha_is_stable_across_openpyxl_modified_time_boundary(tmp_path):
    source = tmp_path / "source.xlsx"
    output_a = tmp_path / "generated-a.xlsx"
    output_b = tmp_path / "generated-b.xlsx"
    _synthetic_n08(source)
    profile = replace(
        N08_0038_OUTPUT_PROFILE,
        source_exemplar_sha256=_file_sha(source),
        fixed_source_bindings=(),
    )
    writer = OpenPyxlWorkbookOutputWriter((profile,))

    first = writer.generate(
        profile_id=profile.profile_id,
        profile_version=profile.profile_version,
        template_path=str(source),
        output_path=str(output_a),
        values=_values(profile),
        source_binding=_binding(),
        generated_at="2026-08-18T08:00:00Z",
    )

    # openpyxl updates the core modified property from wall-clock time during
    # every save. Cross a second boundary deliberately so this proof cannot pass
    # merely because two writes happen inside the same clock tick.
    sleep(1.2)

    second = writer.generate(
        profile_id=profile.profile_id,
        profile_version=profile.profile_version,
        template_path=str(source),
        output_path=str(output_b),
        values=_values(profile),
        source_binding=_binding(),
        generated_at="2026-08-18T08:00:00Z",
    )

    assert first.output_sha256 == _file_sha(output_a)
    assert second.output_sha256 == _file_sha(output_b)
    assert first.output_sha256 == second.output_sha256
    assert output_a.read_bytes() == output_b.read_bytes()
