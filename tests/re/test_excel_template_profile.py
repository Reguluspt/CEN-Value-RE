from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

import pytest

from src.re.adapters.excel import (
    CellClass,
    CompatibilityTransformation,
    ExternalLinkState,
    FingerprintIssueLevel,
    FingerprintStatus,
    FormulaAlternative,
    FormulaObservation,
    N08_0038_PROFILE,
    SheetObservation,
    SheetState,
    UnsupportedTemplateError,
    WorkbookFingerprintObservation,
    formula_signature_digest,
    match_template_profile,
    normalize_formula,
    sheet_state_digest,
)


def _exemplar(
    *,
    filename: str | None = N08_0038_PROFILE.source_exemplar,
    external_link_state: ExternalLinkState = ExternalLinkState.KNOWN_STALE_SELF_REFERENCE,
) -> WorkbookFingerprintObservation:
    return WorkbookFingerprintObservation(
        sheets=tuple(
            SheetObservation(item.name, item.state)
            for item in N08_0038_PROFILE.required_sheets
        ),
        formulas=tuple(
            FormulaObservation(item.cell, item.formula)
            for item in N08_0038_PROFILE.formula_signatures
        ),
        external_link_state=external_link_state,
        filename=filename,
    )


def _replace_formula(
    observation: WorkbookFingerprintObservation,
    cell: str,
    formula: str,
) -> WorkbookFingerprintObservation:
    return replace(
        observation,
        formulas=tuple(
            FormulaObservation(item.cell, formula if item.cell == cell else item.formula)
            for item in observation.formulas
        ),
    )


def test_n08_exemplar_structural_observation_matches_profile() -> None:
    result = match_template_profile(N08_0038_PROFILE, _exemplar())

    assert result.status is FingerprintStatus.MATCHED
    assert result.supported is True
    assert not result.errors
    assert {issue.code for issue in result.warnings} == {
        "EXTERNAL_LINK_STATE_WARNING"
    }
    assert result.profile_sheet_digest == result.observed_sheet_digest
    assert result.profile_formula_digest == result.observed_formula_digest


def test_filename_is_metadata_warning_not_template_identity() -> None:
    result = match_template_profile(
        N08_0038_PROFILE,
        _exemplar(
            filename="renamed-for-approval.xlsx",
            external_link_state=ExternalLinkState.NONE,
        ),
    )

    assert result.supported
    assert not result.errors
    assert {issue.code for issue in result.warnings} == {
        "METADATA_FILENAME_DIFFERENT"
    }


def test_deliberate_required_formula_mutation_is_rejected_fail_closed() -> None:
    observation = _replace_formula(
        _exemplar(external_link_state=ExternalLinkState.NONE),
        "Bangtinh!H119",
        "=ROUND(Sheet1!G18,-4)",
    )
    result = match_template_profile(N08_0038_PROFILE, observation)

    assert result.status is FingerprintStatus.UNSUPPORTED_TEMPLATE
    assert any(issue.code == "FORMULA_SIGNATURE_MISMATCH" for issue in result.errors)
    with pytest.raises(UnsupportedTemplateError, match="UNSUPPORTED_TEMPLATE"):
        result.require_supported()


def test_malformed_required_formula_returns_unsupported_instead_of_raising() -> None:
    observation = _replace_formula(
        _exemplar(external_link_state=ExternalLinkState.NONE),
        "Bangtinh!H119",
        '=IF(A1="unterminated,1,0)',
    )

    result = match_template_profile(N08_0038_PROFILE, observation)

    assert not result.supported
    assert any(issue.code == "FORMULA_INVALID" for issue in result.errors)
    assert len(result.observed_formula_digest) == 64


def test_required_formula_missing_is_rejected() -> None:
    exemplar = _exemplar(external_link_state=ExternalLinkState.NONE)
    observation = replace(
        exemplar,
        formulas=tuple(
            item for item in exemplar.formulas if item.cell != "Bangtinh!G182"
        ),
    )
    result = match_template_profile(N08_0038_PROFILE, observation)

    assert not result.supported
    assert any(issue.code == "FORMULA_SIGNATURE_MISSING" for issue in result.errors)


def test_formula_normalization_ignores_case_and_whitespace_outside_literals() -> None:
    assert normalize_formula(" round( Sheet1!G18 , -3 ) ") == "=ROUND(SHEET1!G18,-3)"
    assert normalize_formula("=ROUND(SHEET1!G18,-3)") == "=ROUND(SHEET1!G18,-3)"


def test_formula_normalization_preserves_excel_string_literal_semantics() -> None:
    expected = normalize_formula('=IF(\'Hồ sơ\'!G14="Shinhan",1,0)')
    changed_literal = normalize_formula('=if(\'Hồ sơ\'!g14="shinhan",1,0)')

    assert expected != changed_literal


def test_formula_normalization_preserves_spaces_inside_quoted_sheet_name() -> None:
    assert normalize_formula("='My Sheet'!a1 + 1") == "='My Sheet'!A1+1"


def test_formula_normalization_rejects_unterminated_literals() -> None:
    with pytest.raises(ValueError, match="unterminated Excel string"):
        normalize_formula('=IF(A1="bad,1,0)')
    with pytest.raises(ValueError, match="quoted sheet"):
        normalize_formula("='Bad Sheet!A1")


def test_missing_required_sheet_is_rejected() -> None:
    exemplar = _exemplar(external_link_state=ExternalLinkState.NONE)
    observation = replace(
        exemplar,
        sheets=tuple(item for item in exemplar.sheets if item.name != "Bangtinh"),
    )

    result = match_template_profile(N08_0038_PROFILE, observation)

    assert not result.supported
    assert any(issue.code == "REQUIRED_SHEET_MISSING" for issue in result.errors)


def test_sheet_state_mutation_is_rejected() -> None:
    exemplar = _exemplar(external_link_state=ExternalLinkState.NONE)
    observation = replace(
        exemplar,
        sheets=tuple(
            SheetObservation(
                item.name,
                SheetState.VISIBLE if item.name == "Sheet1" else item.state,
            )
            for item in exemplar.sheets
        ),
    )

    result = match_template_profile(N08_0038_PROFILE, observation)

    assert not result.supported
    assert any(issue.code == "SHEET_STATE_MISMATCH" for issue in result.errors)


def test_unknown_extra_sheet_is_rejected() -> None:
    exemplar = _exemplar(external_link_state=ExternalLinkState.NONE)
    observation = replace(
        exemplar,
        sheets=exemplar.sheets + (SheetObservation("Unexpected", SheetState.VISIBLE),),
    )

    result = match_template_profile(N08_0038_PROFILE, observation)

    assert not result.supported
    assert any(issue.code == "UNKNOWN_EXTRA_SHEET" for issue in result.errors)


def test_sheet_order_is_not_used_as_identity_when_names_and_states_match() -> None:
    exemplar = _exemplar(external_link_state=ExternalLinkState.NONE)
    observation = replace(exemplar, sheets=tuple(reversed(exemplar.sheets)))

    result = match_template_profile(N08_0038_PROFILE, observation)

    assert result.supported
    assert result.profile_sheet_digest == result.observed_sheet_digest


@pytest.mark.parametrize(
    "state",
    [
        ExternalLinkState.UNKNOWN,
        ExternalLinkState.UNKNOWN_AFFECTING_REQUIRED_OUTPUTS,
        ExternalLinkState.ALLOWED_DECLARED,
    ],
)
def test_undeclared_external_link_state_is_rejected(state: ExternalLinkState) -> None:
    result = match_template_profile(
        N08_0038_PROFILE,
        _exemplar(external_link_state=state),
    )

    assert not result.supported
    assert any(
        issue.code == "EXTERNAL_LINK_STATE_UNSUPPORTED" for issue in result.errors
    )


def test_known_stale_external_reference_is_allowed_but_warned() -> None:
    result = match_template_profile(N08_0038_PROFILE, _exemplar())

    warning = next(
        issue for issue in result.warnings if issue.code == "EXTERNAL_LINK_STATE_WARNING"
    )
    assert warning.level is FingerprintIssueLevel.WARNING


def test_transformed_workbook_with_no_external_link_is_supported() -> None:
    result = match_template_profile(
        N08_0038_PROFILE,
        _exemplar(external_link_state=ExternalLinkState.NONE),
    )

    assert result.supported
    assert not result.warnings


def test_required_control_schema_fails_closed_when_declared_control_is_missing() -> None:
    profile = replace(N08_0038_PROFILE, required_controls=("WalkingSkeletonControl",))
    result = match_template_profile(
        profile,
        _exemplar(external_link_state=ExternalLinkState.NONE),
    )

    assert not result.supported
    assert any(issue.code == "REQUIRED_CONTROL_MISSING" for issue in result.errors)


def test_required_control_schema_accepts_declared_control_when_observed() -> None:
    profile = replace(N08_0038_PROFILE, required_controls=("WalkingSkeletonControl",))
    observation = replace(
        _exemplar(external_link_state=ExternalLinkState.NONE),
        controls=frozenset({"WalkingSkeletonControl"}),
    )

    assert match_template_profile(profile, observation).supported


def test_transformation_metadata_alone_does_not_bypass_formula_mismatch() -> None:
    observation = _replace_formula(
        _exemplar(external_link_state=ExternalLinkState.NONE),
        "Bangtinh!H127",
        "=1",
    )

    result = match_template_profile(N08_0038_PROFILE, observation)

    assert not result.supported
    assert any(issue.code == "FORMULA_SIGNATURE_MISMATCH" for issue in result.errors)


def test_only_exact_declared_formula_alternative_can_pass_transformation_exception() -> None:
    profile = replace(
        N08_0038_PROFILE,
        compatibility_transformations=N08_0038_PROFILE.compatibility_transformations
        + (
            CompatibilityTransformation(
                transformation_id="test-exact-alternate",
                description="Test-only exact compatibility signature.",
                affected_cells=("Bangtinh!H119",),
                accepted_formula_alternatives=(
                    FormulaAlternative("Bangtinh!H119", "=ROUND(Sheet1!G18,-2)"),
                ),
            ),
        ),
    )
    exact = _replace_formula(
        _exemplar(external_link_state=ExternalLinkState.NONE),
        "Bangtinh!H119",
        "=round( Sheet1!G18, -2 )",
    )
    arbitrary = _replace_formula(exact, "Bangtinh!H119", "=1")

    exact_result = match_template_profile(profile, exact)
    arbitrary_result = match_template_profile(profile, arbitrary)

    assert exact_result.supported
    assert any(issue.code == "DECLARED_COMPAT_TRANSFORM" for issue in exact_result.warnings)
    assert not arbitrary_result.supported


def test_signature_digests_are_order_independent_and_semantics_sensitive() -> None:
    exemplar = _exemplar(external_link_state=ExternalLinkState.NONE)

    assert sheet_state_digest(exemplar.sheets) == sheet_state_digest(
        tuple(reversed(exemplar.sheets))
    )
    assert formula_signature_digest(exemplar.formulas) == formula_signature_digest(
        tuple(reversed(exemplar.formulas))
    )

    mutated = _replace_formula(exemplar, "Bangtinh!G182", "=ROUND(G181,-5)")
    assert formula_signature_digest(exemplar.formulas) != formula_signature_digest(
        mutated.formulas
    )


def test_unknown_cells_default_to_read_only_unknown_class() -> None:
    assert N08_0038_PROFILE.cell_class_for("Bangtinh!H119") is CellClass.OUTPUT_CHECKPOINT
    assert (
        N08_0038_PROFILE.cell_class_for("Phieu TTTT!E5")
        is CellClass.VOLATILE_COMPAT_OVERRIDE
    )
    assert N08_0038_PROFILE.cell_class_for("Unknown!A1") is CellClass.UNKNOWN


def test_frozen_source_fingerprint_provenance_is_preserved() -> None:
    assert (
        N08_0038_PROFILE.source_sheet_state_sha256
        == "481997e9672fa4fa88a8b00cb677280e72916b5ce29fde0625f508409ab5e951"
    )
    assert (
        N08_0038_PROFILE.source_formula_checkpoint_sha256
        == "05812836786218f2893feeb065e271b515b777aa8b3b5965dcc8c9819a4e2d7d"
    )
    assert len(N08_0038_PROFILE.required_sheets) == 16
    assert len(N08_0038_PROFILE.formula_signatures) == 24


def test_profile_infrastructure_has_no_workbook_runtime_dependency() -> None:
    excel_root = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "re"
        / "adapters"
        / "excel"
    )
    forbidden = {"openpyxl", "win32com", "pythoncom", "xlwings", "pandas"}
    violations: list[str] = []

    for path in sorted(excel_root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name.split(".", 1)[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module.split(".", 1)[0]]
            else:
                continue
            for module in modules:
                if module in forbidden:
                    violations.append(f"{path.name}:{node.lineno} -> {module}")

    assert not violations, "Workbook runtime dependency entered E0-PR-004: " + ", ".join(
        violations
    )
