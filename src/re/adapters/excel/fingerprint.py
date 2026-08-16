"""Fail-closed Excel template fingerprint matching.

E0-PR-004 operates on declarative workbook observations.  Reading or writing
an actual workbook belongs to a later adapter layer; this module deliberately
has no openpyxl/COM dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

from .profile import (
    ExcelTemplateProfile,
    ExternalLinkState,
    FormulaSignature,
    SheetState,
)


def normalize_formula(formula: str) -> str:
    """Normalize insignificant Excel formula spelling without changing literals.

    - a leading ``=`` is canonicalized;
    - whitespace and case outside quoted string/sheet literals are normalized;
    - text inside double-quoted Excel string constants is preserved exactly;
    - text inside single-quoted sheet names is preserved exactly.

    Locale separators, absolute-reference markers and literal values are not
    rewritten because doing so could hide a semantic mutation.
    """

    text = formula.strip()
    if not text:
        raise ValueError("formula must not be blank")
    if not text.startswith("="):
        text = "=" + text

    out: list[str] = []
    in_string = False
    in_sheet_quote = False
    index = 0

    while index < len(text):
        char = text[index]

        if in_string:
            out.append(char)
            if char == '"':
                if index + 1 < len(text) and text[index + 1] == '"':
                    out.append('"')
                    index += 2
                    continue
                in_string = False
            index += 1
            continue

        if in_sheet_quote:
            out.append(char)
            if char == "'":
                if index + 1 < len(text) and text[index + 1] == "'":
                    out.append("'")
                    index += 2
                    continue
                in_sheet_quote = False
            index += 1
            continue

        if char == '"':
            in_string = True
            out.append(char)
        elif char == "'":
            in_sheet_quote = True
            out.append(char)
        elif char.isspace():
            pass
        else:
            out.append(char.upper())
        index += 1

    if in_string:
        raise ValueError("unterminated Excel string literal")
    if in_sheet_quote:
        raise ValueError("unterminated quoted sheet name")
    return "".join(out)


def _normalize_cell(cell: str) -> str:
    text = cell.strip()
    if "!" not in text:
        raise ValueError("cell reference must use Sheet!A1 form")
    sheet, coordinate = text.rsplit("!", 1)
    if not sheet or not coordinate:
        raise ValueError("cell reference must use Sheet!A1 form")
    return f"{sheet}!{coordinate.upper()}"


@dataclass(frozen=True, slots=True)
class SheetObservation:
    name: str
    state: SheetState


@dataclass(frozen=True, slots=True)
class FormulaObservation:
    cell: str
    formula: str


@dataclass(frozen=True, slots=True)
class WorkbookFingerprintObservation:
    sheets: tuple[SheetObservation, ...]
    formulas: tuple[FormulaObservation, ...]
    external_link_state: ExternalLinkState
    controls: frozenset[str] = frozenset()
    filename: str | None = None

    def __post_init__(self) -> None:
        sheet_names = [item.name for item in self.sheets]
        if len(set(sheet_names)) != len(sheet_names):
            raise ValueError("observed sheet names must be unique")

        formula_cells = [_normalize_cell(item.cell) for item in self.formulas]
        if len(set(formula_cells)) != len(formula_cells):
            raise ValueError("observed formula cells must be unique")


class FingerprintStatus(str, Enum):
    MATCHED = "MATCHED"
    UNSUPPORTED_TEMPLATE = "UNSUPPORTED_TEMPLATE"


class FingerprintIssueLevel(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True, slots=True)
class FingerprintIssue:
    level: FingerprintIssueLevel
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class FingerprintMatchResult:
    profile_id: str
    profile_version: str
    status: FingerprintStatus
    issues: tuple[FingerprintIssue, ...]
    profile_sheet_digest: str
    observed_sheet_digest: str
    profile_formula_digest: str
    observed_formula_digest: str

    @property
    def supported(self) -> bool:
        return self.status is FingerprintStatus.MATCHED

    @property
    def errors(self) -> tuple[FingerprintIssue, ...]:
        return tuple(
            issue for issue in self.issues if issue.level is FingerprintIssueLevel.ERROR
        )

    @property
    def warnings(self) -> tuple[FingerprintIssue, ...]:
        return tuple(
            issue
            for issue in self.issues
            if issue.level is FingerprintIssueLevel.WARNING
        )

    def require_supported(self) -> "FingerprintMatchResult":
        if not self.supported:
            raise UnsupportedTemplateError(self)
        return self


class UnsupportedTemplateError(ValueError):
    def __init__(self, result: FingerprintMatchResult):
        self.result = result
        detail = "; ".join(issue.message for issue in result.errors)
        super().__init__(f"UNSUPPORTED_TEMPLATE: {detail}")


def sheet_state_digest(
    sheets: tuple[SheetObservation, ...] | tuple[object, ...],
) -> str:
    rows: list[str] = []
    for item in sheets:
        name = getattr(item, "name")
        state = getattr(item, "state")
        state_value = state.value if isinstance(state, SheetState) else str(state)
        rows.append(f"{name}\t{state_value}")
    payload = "\n".join(sorted(rows)).encode("utf-8")
    return sha256(payload).hexdigest()


def formula_signature_digest(
    signatures: tuple[FormulaObservation, ...] | tuple[FormulaSignature, ...],
) -> str:
    rows = [
        f"{_normalize_cell(item.cell)}\t{normalize_formula(item.formula)}"
        for item in signatures
    ]
    payload = "\n".join(sorted(rows)).encode("utf-8")
    return sha256(payload).hexdigest()


def _safe_observed_formula_digest(
    signatures: tuple[FormulaObservation, ...],
) -> str:
    try:
        return formula_signature_digest(signatures)
    except ValueError:
        rows = [
            f"{_normalize_cell(item.cell)}\tINVALID\t{item.formula}"
            for item in signatures
        ]
        return sha256("\n".join(sorted(rows)).encode("utf-8")).hexdigest()


def _issue(
    issues: list[FingerprintIssue],
    level: FingerprintIssueLevel,
    code: str,
    message: str,
) -> None:
    issues.append(FingerprintIssue(level=level, code=code, message=message))


def match_template_profile(
    profile: ExcelTemplateProfile,
    observation: WorkbookFingerprintObservation,
) -> FingerprintMatchResult:
    """Compare one observation to one profile using fail-closed structural rules."""

    issues: list[FingerprintIssue] = []

    # Filename is metadata only and cannot establish or defeat a structural match.
    if observation.filename and observation.filename != profile.source_exemplar:
        _issue(
            issues,
            FingerprintIssueLevel.WARNING,
            "METADATA_FILENAME_DIFFERENT",
            (
                f"filename {observation.filename!r} differs from source exemplar "
                f"{profile.source_exemplar!r}"
            ),
        )

    expected_sheets = {item.name: item.state for item in profile.required_sheets}
    observed_sheets = {item.name: item.state for item in observation.sheets}

    for name, state in expected_sheets.items():
        if name not in observed_sheets:
            _issue(
                issues,
                FingerprintIssueLevel.ERROR,
                "REQUIRED_SHEET_MISSING",
                f"required sheet {name!r} is missing",
            )
            continue
        if observed_sheets[name] is not state:
            _issue(
                issues,
                FingerprintIssueLevel.ERROR,
                "SHEET_STATE_MISMATCH",
                (
                    f"sheet {name!r} state is {observed_sheets[name].value!r}; "
                    f"expected {state.value!r}"
                ),
            )

    if not profile.allow_extra_sheets:
        extras = sorted(set(observed_sheets) - set(expected_sheets))
        for name in extras:
            _issue(
                issues,
                FingerprintIssueLevel.ERROR,
                "UNKNOWN_EXTRA_SHEET",
                f"unknown extra sheet {name!r} is not allowed by profile",
            )

    observed_formulas = {
        _normalize_cell(item.cell): item.formula for item in observation.formulas
    }

    for signature in profile.formula_signatures:
        cell = _normalize_cell(signature.cell)
        observed_formula = observed_formulas.get(cell)
        if observed_formula is None:
            _issue(
                issues,
                FingerprintIssueLevel.ERROR,
                "FORMULA_SIGNATURE_MISSING",
                f"required formula signature {cell} is missing",
            )
            continue

        try:
            expected_normalized = normalize_formula(signature.formula)
            observed_normalized = normalize_formula(observed_formula)
            alternate_normalized = {
                normalize_formula(value)
                for value in profile.formula_alternatives_for(signature.cell)
            }
        except ValueError as exc:
            _issue(
                issues,
                FingerprintIssueLevel.ERROR,
                "FORMULA_INVALID",
                f"{cell}: {exc}",
            )
            continue

        if observed_normalized == expected_normalized:
            continue

        if observed_normalized in alternate_normalized:
            _issue(
                issues,
                FingerprintIssueLevel.WARNING,
                "DECLARED_COMPAT_TRANSFORM",
                f"{cell} uses an exact formula alternative declared by the profile",
            )
            continue

        _issue(
            issues,
            FingerprintIssueLevel.ERROR,
            "FORMULA_SIGNATURE_MISMATCH",
            f"normalized formula mismatch at {cell}",
        )

    if observation.external_link_state not in profile.external_link_policy.allowed_states:
        _issue(
            issues,
            FingerprintIssueLevel.ERROR,
            "EXTERNAL_LINK_STATE_UNSUPPORTED",
            (
                f"external-link state {observation.external_link_state.value} "
                "is not allowed by profile"
            ),
        )
    elif observation.external_link_state in profile.external_link_policy.warning_states:
        _issue(
            issues,
            FingerprintIssueLevel.WARNING,
            "EXTERNAL_LINK_STATE_WARNING",
            (
                f"external-link state {observation.external_link_state.value} "
                "is allowed only as a declared compatibility condition"
            ),
        )

    for control in profile.required_controls:
        if control not in observation.controls:
            _issue(
                issues,
                FingerprintIssueLevel.ERROR,
                "REQUIRED_CONTROL_MISSING",
                f"required named/control range {control!r} is missing",
            )

    status = (
        FingerprintStatus.UNSUPPORTED_TEMPLATE
        if any(issue.level is FingerprintIssueLevel.ERROR for issue in issues)
        else FingerprintStatus.MATCHED
    )

    return FingerprintMatchResult(
        profile_id=profile.profile_id,
        profile_version=profile.profile_version,
        status=status,
        issues=tuple(issues),
        profile_sheet_digest=sheet_state_digest(profile.required_sheets),
        observed_sheet_digest=sheet_state_digest(observation.sheets),
        profile_formula_digest=formula_signature_digest(profile.formula_signatures),
        observed_formula_digest=_safe_observed_formula_digest(observation.formulas),
    )
