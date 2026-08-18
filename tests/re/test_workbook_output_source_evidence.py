import json
from pathlib import Path

from src.re.adapters.excel_output.n08_0038 import N08_0038_OUTPUT_PROFILE


_FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "N08_0038_OUTPUT_SOURCE_EVIDENCE_v1.json"
)


def _evidence():
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def test_output_profile_is_bound_to_direct_source_workbook_evidence():
    evidence = _evidence()
    source = evidence["source_workbook"]
    profile = N08_0038_OUTPUT_PROFILE

    assert source["sha256"] == profile.source_exemplar_sha256
    assert source["profile_id"] == profile.profile_id
    assert source["profile_version"] == profile.profile_version

    writable = set(profile.allowed_write_cells)
    formula_backed = set(evidence["formula_backed_read_only_cells"])
    direct_verified = set(evidence["direct_writable_cells_verified"])

    assert writable.isdisjoint(formula_backed - {"Phieu TTTT!E5"})
    assert direct_verified.issubset(writable)


def test_all_33_direct_adjustment_decision_cells_are_profile_writable():
    evidence = _evidence()["adjustment_decision_cells"]
    expected = {
        f"Bangtinh!{column}{row}"
        for column in evidence["columns"]
        for row in evidence["rows"]
    }
    assert len(expected) == evidence["count"] == 33
    assert expected.issubset(N08_0038_OUTPUT_PROFILE.allowed_write_cells)


def test_gate_b10_consumers_match_direct_source_evidence():
    expected = _evidence()["gate_b10_consumers"]
    actual = {
        item.cell: item.expected_formula
        for item in N08_0038_OUTPUT_PROFILE.output_consumers
    }
    assert actual == expected


def test_only_frozen_compatibility_transformation_may_replace_e5_formula():
    evidence = _evidence()["known_compatibility_formula"]
    bindings = {
        item.cell: item.transformation_id
        for item in N08_0038_OUTPUT_PROFILE.compatibility_bindings
    }
    assert bindings == {
        evidence["cell"]: evidence["allowed_transformation_id"]
    }
