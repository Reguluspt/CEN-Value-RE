from __future__ import annotations

from decimal import Decimal, getcontext
import json
from pathlib import Path

import pytest

from src.re.application.services.golden_fixture import (
    CheckpointManifest,
    ComparisonKind,
    GoldenFixtureFormatError,
    compare_checkpoint,
    evaluate_checkpoint_results,
    load_checkpoint_manifest,
    load_golden_bundle,
    load_golden_fixture,
    resolve_json_pointer,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "fixtures" / "GOLDEN_CASE_CANONICAL_FIXTURE_v1.json"
MANIFEST_PATH = ROOT / "fixtures" / "GOLDEN_CASE_CHECKPOINT_MANIFEST_v1.json"

EXPECTED_IDS = (
    "Bangtinh!F108", "Bangtinh!G108", "Bangtinh!H108", "Sheet1!G18", "Bangtinh!H119",
    "quality.TSSS01.adjustment_count", "quality.TSSS02.adjustment_count", "quality.TSSS03.adjustment_count",
    "quality.TSSS01.gross_adjustment_value", "quality.TSSS02.gross_adjustment_value", "quality.TSSS03.gross_adjustment_value",
    "quality.TSSS01.adjustment_amplitude", "quality.TSSS02.adjustment_amplitude", "quality.TSSS03.adjustment_amplitude",
    "quality.TSSS01.net_adjustment_value", "quality.TSSS02.net_adjustment_value", "quality.TSSS03.net_adjustment_value",
    "Bangtinh!H127", "Bangtinh!F140", "Bangtinh!H153", "Bangtinh!G156", "Bangtinh!G157",
    "Bangtinh!H161", "Bangtinh!H163", "Bangtinh!G171", "Bangtinh!G175", "Bangtinh!G169",
    "Bangtinh!G178", "Bangtinh!G181", "Bangtinh!G182", "Offical!E32",
)


def _manifest() -> CheckpointManifest:
    return load_checkpoint_manifest(MANIFEST_PATH)


def _oracle_results(manifest: CheckpointManifest):
    return {item.checkpoint_id: item.expected for item in manifest.checkpoints}


def test_fixture_loads_deterministically_and_remains_partial() -> None:
    first = load_golden_fixture(FIXTURE_PATH); second = load_golden_fixture(FIXTURE_PATH)
    assert first == second
    assert first.fixture_id == "N08-0038-canonical-v1"
    assert first.partial_input_coverage
    assert len(first.semantic_sha256) == 64
    assert resolve_json_pointer(first.payload, "/case/appraisal_date") == "2026-08-05"
    assert resolve_json_pointer(first.payload, "/subject/construction/maintenance_condition_pct") == "0.05"


def test_fixture_semantic_digest_ignores_json_formatting(tmp_path: Path) -> None:
    original = json.loads(FIXTURE_PATH.read_text(encoding="utf-8")); path = tmp_path / "fixture.json"
    path.write_text(json.dumps(original, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    assert load_golden_fixture(FIXTURE_PATH).semantic_sha256 == load_golden_fixture(path).semantic_sha256


def test_fixture_json_rejects_binary_float_tokens(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"; path.write_text('{"fixture_id":"x","status":"PARTIAL INPUT COVERAGE","expected":{"x":0.1}}', encoding="utf-8")
    with pytest.raises(GoldenFixtureFormatError, match="binary-float"): load_golden_fixture(path)


def test_manifest_is_versioned_and_freezes_exact_checkpoint_set() -> None:
    manifest = _manifest()
    assert manifest.manifest_id == "N08-0038-checkpoints-v1"
    assert manifest.version == 1 and manifest.fixture_id == "N08-0038-canonical-v1"
    assert manifest.status == "LEGACY_CACHE_REGRESSION_ORACLE; NOT_EXCEL_QUALIFICATION"
    assert manifest.checkpoint_ids == EXPECTED_IDS and len(manifest.checkpoints) == 31
    assert len(manifest.semantic_sha256) == len(manifest.checkpoint_set_sha256) == 64


def test_manifest_deterministic_digests_repeat() -> None:
    first = _manifest(); second = _manifest()
    assert first.semantic_sha256 == second.semantic_sha256
    assert first.checkpoint_set_sha256 == second.checkpoint_set_sha256


def test_bundle_binds_fixture_expected_values_to_manifest() -> None:
    bundle = load_golden_bundle(FIXTURE_PATH, MANIFEST_PATH)
    assert bundle.fixture.fixture_id == bundle.manifest.fixture_id
    bound = {x.checkpoint_id: x.fixture_pointer for x in bundle.manifest.checkpoints if x.fixture_pointer is not None}
    assert bound == {
        "Bangtinh!F108":"/expected/indicated_prices/0", "Bangtinh!G108":"/expected/indicated_prices/1",
        "Bangtinh!H108":"/expected/indicated_prices/2", "Sheet1!G18":"/expected/selected_indication",
        "Bangtinh!H119":"/expected/rounded_indication", "Bangtinh!H163":"/expected/construction_total",
        "Bangtinh!G169":"/expected/land_total", "Bangtinh!G178":"/expected/construction_total",
        "Bangtinh!G181":"/expected/total_before_rounding", "Bangtinh!G182":"/expected/final_rounded_value",
        "Offical!E32":"/expected/total_before_rounding",
    }


def test_bundle_rejects_fixture_expected_drift_even_within_runtime_tolerance(tmp_path: Path) -> None:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8")); data["expected"]["indicated_prices"][0] = "196308350.4"
    path = tmp_path / "fixture.json"; path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(GoldenFixtureFormatError, match="fixture binding mismatch"): load_golden_bundle(path, MANIFEST_PATH)


def test_bundle_rejects_fixture_id_mismatch(tmp_path: Path) -> None:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8")); data["fixture_id"] = "other"
    path = tmp_path / "fixture.json"; path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(GoldenFixtureFormatError, match="fixture_id mismatch"): load_golden_bundle(path, MANIFEST_PATH)


def test_manifest_rejects_duplicate_checkpoint_id(tmp_path: Path) -> None:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")); data["checkpoints"].append(dict(data["checkpoints"][0])); data["checkpoint_count"] += 1
    path = tmp_path / "manifest.json"; path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(GoldenFixtureFormatError, match="duplicate checkpoint_id"): load_checkpoint_manifest(path)


def test_manifest_rejects_checkpoint_count_drift(tmp_path: Path) -> None:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")); data["checkpoint_count"] = 30
    path = tmp_path / "manifest.json"; path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(GoldenFixtureFormatError, match="checkpoint_count"): load_checkpoint_manifest(path)


def test_manifest_rejects_generic_negative_tolerance(tmp_path: Path) -> None:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")); data["checkpoints"][0]["comparison"]["tolerance"] = "-0.5"
    path = tmp_path / "manifest.json"; path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(GoldenFixtureFormatError, match="non-negative tolerance"): load_checkpoint_manifest(path)


def test_manifest_rejects_non_whole_rounding_increment(tmp_path: Path) -> None:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")); h119 = next(x for x in data["checkpoints"] if x["checkpoint_id"] == "Bangtinh!H119"); h119["comparison"]["rounding_increment"] = "1000.5"
    path = tmp_path / "manifest.json"; path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(GoldenFixtureFormatError, match="whole base-unit"): load_checkpoint_manifest(path)


def test_runtime_tolerance_is_checkpoint_specific() -> None:
    spec = next(x for x in _manifest().checkpoints if x.checkpoint_id == "Bangtinh!F108")
    assert spec.policy.kind is ComparisonKind.ABSOLUTE_TOLERANCE and spec.policy.tolerance == Decimal("0.5")
    assert compare_checkpoint(spec, "196308350.5").passed and compare_checkpoint(spec, "196308349.5").passed
    assert not compare_checkpoint(spec, "196308350.5000001").passed


def test_explicitly_rounded_checkpoint_requires_exact_integer() -> None:
    spec = next(x for x in _manifest().checkpoints if x.checkpoint_id == "Bangtinh!H119")
    assert spec.policy.kind is ComparisonKind.EXACT_INTEGER and spec.policy.rounding_increment == Decimal("1000")
    assert compare_checkpoint(spec, "196308000").passed
    assert not compare_checkpoint(spec, "196308000.1").passed and not compare_checkpoint(spec, "196309000").passed


def test_decimal_scale_checkpoint_uses_declared_scale_not_global_epsilon() -> None:
    spec = next(x for x in _manifest().checkpoints if x.checkpoint_id == "Bangtinh!H127")
    assert spec.policy.kind is ComparisonKind.DECIMAL_SCALE and spec.policy.scale == 2
    assert compare_checkpoint(spec, "0.694").passed and not compare_checkpoint(spec, "0.695").passed


def test_decimal_scale_comparison_is_independent_of_ambient_decimal_precision() -> None:
    spec = next(x for x in _manifest().checkpoints if x.checkpoint_id == "Bangtinh!H127"); prior = getcontext().prec
    try:
        getcontext().prec = 2; assert compare_checkpoint(spec, "0.69").passed
    finally: getcontext().prec = prior


def test_adjustment_amplitude_preserves_nonzero_range_as_text() -> None:
    specs = {x.checkpoint_id:x for x in _manifest().checkpoints if x.checkpoint_id.endswith(".adjustment_amplitude")}
    assert [specs[f"quality.TSSS0{i}.adjustment_amplitude"].expected for i in (1,2,3)] == ["5–10","5–15","3–5"]
    assert compare_checkpoint(specs["quality.TSSS01.adjustment_amplitude"], "5–10").passed
    assert not compare_checkpoint(specs["quality.TSSS01.adjustment_amplitude"], "0–10").passed


def test_pre_rounding_and_final_rounded_outputs_are_distinct_checkpoints() -> None:
    specs = {x.checkpoint_id:x for x in _manifest().checkpoints}
    assert specs["Bangtinh!G181"].expected == specs["Offical!E32"].expected == Decimal("19581412440")
    assert specs["Bangtinh!G182"].expected == Decimal("19581000000")
    assert specs["Bangtinh!G182"].policy.rounding_increment == Decimal("1000000")


def test_full_oracle_result_map_passes_without_excel() -> None:
    manifest = _manifest(); report = evaluate_checkpoint_results(manifest, _oracle_results(manifest))
    assert report.passed and report.passed_count == 31 and report.failed_count == 0
    assert report.missing_checkpoint_ids == report.unexpected_checkpoint_ids == ()


def test_one_mutated_checkpoint_fails_report() -> None:
    manifest = _manifest(); actual = _oracle_results(manifest); actual["Bangtinh!G182"] = "19582000000"
    report = evaluate_checkpoint_results(manifest, actual)
    assert not report.passed
    assert [x.checkpoint_id for x in report.outcomes if not x.passed] == ["Bangtinh!G182"]


def test_missing_checkpoint_fails_closed() -> None:
    manifest = _manifest(); actual = _oracle_results(manifest); actual.pop("Bangtinh!H119"); report = evaluate_checkpoint_results(manifest, actual)
    assert not report.passed and report.missing_checkpoint_ids == ("Bangtinh!H119",)


def test_unexpected_checkpoint_fails_in_strict_mode() -> None:
    manifest = _manifest(); actual = _oracle_results(manifest); actual["unknown.checkpoint"] = "1"; report = evaluate_checkpoint_results(manifest, actual)
    assert not report.passed and report.unexpected_checkpoint_ids == ("unknown.checkpoint",)


def test_unexpected_checkpoint_can_be_reported_non_strictly_without_hiding_required_set() -> None:
    manifest = _manifest(); actual = _oracle_results(manifest); actual["diagnostic.extra"] = "1"
    report = evaluate_checkpoint_results(manifest, actual, strict_checkpoint_set=False)
    assert report.passed and report.unexpected_checkpoint_ids == ("diagnostic.extra",) and report.passed_count == 31


def test_binary_float_actual_is_rejected_per_checkpoint() -> None:
    manifest = _manifest(); actual = _oracle_results(manifest); actual["Bangtinh!F108"] = 196308350.0; report = evaluate_checkpoint_results(manifest, actual)
    outcome = next(x for x in report.outcomes if x.checkpoint_id == "Bangtinh!F108")
    assert not outcome.passed and "binary float" in outcome.reason


def test_nonfinite_actual_is_rejected_per_checkpoint() -> None:
    manifest = _manifest(); actual = _oracle_results(manifest); actual["Bangtinh!F108"] = "NaN"; report = evaluate_checkpoint_results(manifest, actual)
    outcome = next(x for x in report.outcomes if x.checkpoint_id == "Bangtinh!F108")
    assert not outcome.passed and "finite" in outcome.reason


def test_report_order_and_digest_are_deterministic() -> None:
    manifest = _manifest(); actual = _oracle_results(manifest)
    first = evaluate_checkpoint_results(manifest, actual); second = evaluate_checkpoint_results(manifest, dict(reversed(list(actual.items()))))
    assert first == second and tuple(x.checkpoint_id for x in first.outcomes) == EXPECTED_IDS


def test_resolve_json_pointer_handles_array_entries() -> None:
    fixture = load_golden_fixture(FIXTURE_PATH)
    assert resolve_json_pointer(fixture.payload, "/expected/indicated_prices/2") == "212201640"


def test_resolve_json_pointer_fails_closed_for_missing_path() -> None:
    fixture = load_golden_fixture(FIXTURE_PATH)
    with pytest.raises(GoldenFixtureFormatError, match="not found"): resolve_json_pointer(fixture.payload, "/expected/not_here")


def test_harness_module_contains_no_excel_runtime_or_binary_float_dependency() -> None:
    import ast
    module_path = ROOT / "src" / "re" / "application" / "services" / "golden_fixture.py"; source = module_path.read_text(encoding="utf-8")
    for forbidden in ("openpyxl", "xlwings", "win32com", "pandas"): assert forbidden not in source
    tree = ast.parse(source, filename=str(module_path))
    assert not [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "float"]
