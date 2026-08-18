"""N08-0038 output-write contract for the Epic-1 Walking Skeleton."""

from __future__ import annotations

from ..excel.n08_0038 import N08_0038_PROFILE
from .profile import (
    WorkbookCompatibilityBinding,
    WorkbookFixedSourceBinding,
    WorkbookOutputConsumer,
    WorkbookOutputProfile,
    WorkbookValueKind,
    WorkbookWriteBinding,
)


def _binding(cell: str, source_key: str, kind: WorkbookValueKind) -> WorkbookWriteBinding:
    return WorkbookWriteBinding(cell=cell, source_key=source_key, value_kind=kind)


def _fixed(cell: str, source_key: str, kind: WorkbookValueKind) -> WorkbookFixedSourceBinding:
    return WorkbookFixedSourceBinding(cell=cell, source_key=source_key, value_kind=kind)


_N08_SUBJECT_BINDINGS = (
    _binding("Nhập liệu!F7", "subject.current_address", WorkbookValueKind.TEXT),
    _binding("Nhập liệu!F9", "subject.province", WorkbookValueKind.TEXT),
    _binding("Nhập liệu!G16", "subject.latitude", WorkbookValueKind.DECIMAL),
    _binding("Nhập liệu!G17", "subject.longitude", WorkbookValueKind.DECIMAL),
    _binding("Nhập liệu!G18", "subject.parcel_number", WorkbookValueKind.TEXT),
    _binding("Nhập liệu!K18", "subject.map_sheet_number", WorkbookValueKind.TEXT),
    _binding("Nhập liệu!F42", "subject.noncompliant_area_m2", WorkbookValueKind.DECIMAL),
    _binding("Nhập liệu!H46", "subject.frontage", WorkbookValueKind.DECIMAL),
    _binding("Nhập liệu!H48", "subject.shape", WorkbookValueKind.TEXT),
)

# The exemplar contains case-specific formula-backed legacy inputs.  Gate B did
# not authorize rewriting those formulas, so E1-PR-005 accepts the profile only
# when current canonical values match the cached exemplar state.
_N08_FIXED_SUBJECT_BINDINGS = (
    _fixed("Nhập liệu!F36", "subject.total_area_m2", WorkbookValueKind.DECIMAL),
    _fixed("Nhập liệu!I31", "subject.noncompliant_unit_price", WorkbookValueKind.DECIMAL),
    _fixed("Nhập liệu!H47", "subject.depth", WorkbookValueKind.DECIMAL),
)


_N08_COMPARABLE_BINDINGS = (
    # TSSS01 writable cells
    _binding("Phieu TTTT!B15", "comparable.1.asking_price", WorkbookValueKind.DECIMAL),
    _binding("Phieu TTTT!B19", "comparable.1.transaction_success_factor", WorkbookValueKind.FRACTION),
    _binding("Phieu TTTT!D34", "comparable.1.frontage", WorkbookValueKind.DECIMAL),
    _binding("Phieu TTTT!D38", "comparable.1.shape", WorkbookValueKind.TEXT),
    _binding("Phieu TTTT!B55", "comparable.1.building_area_m2", WorkbookValueKind.DECIMAL),
    _binding("Phieu TTTT!B58", "comparable.1.building_remaining_quality", WorkbookValueKind.FRACTION),
    # TSSS02 writable cells
    _binding("Phieu TTTT!G15", "comparable.2.asking_price", WorkbookValueKind.DECIMAL),
    _binding("Phieu TTTT!G19", "comparable.2.transaction_success_factor", WorkbookValueKind.FRACTION),
    _binding("Phieu TTTT!I34", "comparable.2.frontage", WorkbookValueKind.DECIMAL),
    _binding("Phieu TTTT!I35", "comparable.2.depth", WorkbookValueKind.DECIMAL),
    _binding("Phieu TTTT!I38", "comparable.2.shape", WorkbookValueKind.TEXT),
    _binding("Phieu TTTT!G55", "comparable.2.building_area_m2", WorkbookValueKind.DECIMAL),
    _binding("Phieu TTTT!G58", "comparable.2.building_remaining_quality", WorkbookValueKind.FRACTION),
    # TSSS03 writable cells
    _binding("Phieu TTTT!L15", "comparable.3.asking_price", WorkbookValueKind.DECIMAL),
    _binding("Phieu TTTT!L19", "comparable.3.transaction_success_factor", WorkbookValueKind.FRACTION),
    _binding("Phieu TTTT!N34", "comparable.3.frontage", WorkbookValueKind.DECIMAL),
    _binding("Phieu TTTT!N38", "comparable.3.shape", WorkbookValueKind.TEXT),
    _binding("Phieu TTTT!L58", "comparable.3.building_remaining_quality", WorkbookValueKind.FRACTION),
)

_N08_FIXED_COMPARABLE_BINDINGS = (
    _fixed("Phieu TTTT!D29", "comparable.1.area_m2", WorkbookValueKind.DECIMAL),
    _fixed("Phieu TTTT!D35", "comparable.1.depth", WorkbookValueKind.DECIMAL),
    _fixed("Phieu TTTT!I29", "comparable.2.area_m2", WorkbookValueKind.DECIMAL),
    _fixed("Phieu TTTT!N29", "comparable.3.area_m2", WorkbookValueKind.DECIMAL),
    _fixed("Phieu TTTT!N35", "comparable.3.depth", WorkbookValueKind.DECIMAL),
    _fixed("Phieu TTTT!L55", "comparable.3.building_area_m2", WorkbookValueKind.DECIMAL),
)


_RATE_ROWS = (55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105)
_N08_ADJUSTMENT_BINDINGS = tuple(
    _binding(
        f"Bangtinh!{column}{row}",
        f"adjustment.{order}.C{factor}.selected_rate",
        WorkbookValueKind.FRACTION,
    )
    for order, column in ((1, "F"), (2, "G"), (3, "H"))
    for factor, row in enumerate(_RATE_ROWS, 1)
)


N08_0038_OUTPUT_PROFILE = WorkbookOutputProfile(
    template_profile=N08_0038_PROFILE,
    source_exemplar_sha256="d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c",
    write_bindings=(
        *_N08_SUBJECT_BINDINGS,
        *_N08_COMPARABLE_BINDINGS,
        *_N08_ADJUSTMENT_BINDINGS,
    ),
    fixed_source_bindings=(
        *_N08_FIXED_SUBJECT_BINDINGS,
        *_N08_FIXED_COMPARABLE_BINDINGS,
    ),
    compatibility_bindings=(
        WorkbookCompatibilityBinding(
            transformation_id="localize-stale-phieu-tttt-e5",
            cell="Phieu TTTT!E5",
            source_key="subject.province",
            value_kind=WorkbookValueKind.TEXT,
        ),
    ),
    output_consumers=(
        WorkbookOutputConsumer(
            cell="Bangtinh!G181",
            semantic_key="total_value_before_rounding_vnd",
            expected_formula="=ROUND(G169+G178,0)",
        ),
        WorkbookOutputConsumer(
            cell="Bangtinh!G182",
            semantic_key="final_appraised_value_vnd",
            expected_formula="=ROUND(G181,-6)",
        ),
        WorkbookOutputConsumer(
            cell="Offical!E32",
            semantic_key="total_value_before_rounding_vnd",
            expected_formula="=Bangtinh!G181",
        ),
    ),
)
