"""Declarative Excel template-profile schema for CenValue RE.

This module contains no workbook runtime dependency.  It describes the
compatibility contract consumed by fingerprint/read-write adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CellClass(str, Enum):
    """Safety class for a workbook cell."""

    INPUT = "INPUT"
    FORMULA_PROTECTED = "FORMULA_PROTECTED"
    OUTPUT_CHECKPOINT = "OUTPUT_CHECKPOINT"
    CONTROL = "CONTROL"
    APPROVAL_RETURN = "APPROVAL_RETURN"
    VOLATILE_COMPAT_OVERRIDE = "VOLATILE_COMPAT_OVERRIDE"
    UNKNOWN = "UNKNOWN"


class SheetState(str, Enum):
    VISIBLE = "visible"
    HIDDEN = "hidden"
    VERY_HIDDEN = "veryHidden"


class ExternalLinkState(str, Enum):
    """Profile-level external-link classification, not a raw URL list."""

    NONE = "NONE"
    KNOWN_STALE_SELF_REFERENCE = "KNOWN_STALE_SELF_REFERENCE"
    ALLOWED_DECLARED = "ALLOWED_DECLARED"
    UNKNOWN_AFFECTING_REQUIRED_OUTPUTS = "UNKNOWN_AFFECTING_REQUIRED_OUTPUTS"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class SheetRequirement:
    name: str
    state: SheetState

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("sheet name must not be blank")


@dataclass(frozen=True, slots=True)
class CellRule:
    cell: str
    cell_class: CellClass

    def __post_init__(self) -> None:
        if "!" not in self.cell or not self.cell.strip():
            raise ValueError("cell rule must use Sheet!A1 form")


@dataclass(frozen=True, slots=True)
class FormulaSignature:
    cell: str
    formula: str

    def __post_init__(self) -> None:
        if "!" not in self.cell or not self.cell.strip():
            raise ValueError("formula signature must use Sheet!A1 form")
        if not self.formula.strip():
            raise ValueError("formula signature must not be blank")


@dataclass(frozen=True, slots=True)
class FormulaAlternative:
    """Exact alternate formula admitted by one declared transformation."""

    cell: str
    formula: str

    def __post_init__(self) -> None:
        if "!" not in self.cell or not self.cell.strip():
            raise ValueError("formula alternative must use Sheet!A1 form")
        if not self.formula.strip():
            raise ValueError("formula alternative must not be blank")


@dataclass(frozen=True, slots=True)
class CompatibilityTransformation:
    transformation_id: str
    description: str
    affected_cells: tuple[str, ...] = ()
    accepted_formula_alternatives: tuple[FormulaAlternative, ...] = ()

    def __post_init__(self) -> None:
        if not self.transformation_id.strip():
            raise ValueError("transformation_id must not be blank")
        if not self.description.strip():
            raise ValueError("transformation description must not be blank")
        if len(set(self.affected_cells)) != len(self.affected_cells):
            raise ValueError("affected_cells must be unique")
        for alternative in self.accepted_formula_alternatives:
            if alternative.cell not in self.affected_cells:
                raise ValueError(
                    "formula alternative cell must be declared in affected_cells"
                )


@dataclass(frozen=True, slots=True)
class ExternalLinkPolicy:
    allowed_states: frozenset[ExternalLinkState]
    warning_states: frozenset[ExternalLinkState] = frozenset()

    def __post_init__(self) -> None:
        if not self.allowed_states:
            raise ValueError("external-link policy requires at least one allowed state")
        if not self.warning_states.issubset(self.allowed_states):
            raise ValueError("warning states must also be allowed states")


@dataclass(frozen=True, slots=True)
class TemplateRoundingDefault:
    """Trusted rounding default declared by one frozen template profile."""

    target: str
    mode: str
    increment_vnd: int | None

    def __post_init__(self) -> None:
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("rounding target must be a non-empty string")
        if self.target != self.target.strip():
            raise ValueError("rounding target must be trimmed")
        if not isinstance(self.mode, str) or not self.mode.strip():
            raise ValueError("rounding mode must be a non-empty string")
        if self.mode != self.mode.strip():
            raise ValueError("rounding mode must be trimmed")
        if self.increment_vnd is not None:
            if isinstance(self.increment_vnd, bool) or not isinstance(
                self.increment_vnd, int
            ):
                raise TypeError("rounding increment must be a whole-VND integer or None")
            if self.increment_vnd <= 0:
                raise ValueError("rounding increment must be positive")


@dataclass(frozen=True, slots=True)
class ExcelTemplateProfile:
    """Immutable compatibility profile.

    ``source_*_sha256`` values are provenance from the frozen Gate-B
    fingerprint.  E0-PR-004 computes its own deterministic normalized
    digests at runtime rather than assuming the historical hash algorithm.
    """

    profile_id: str
    profile_version: str
    source_exemplar: str
    required_sheets: tuple[SheetRequirement, ...]
    formula_signatures: tuple[FormulaSignature, ...]
    cell_rules: tuple[CellRule, ...] = ()
    compatibility_transformations: tuple[CompatibilityTransformation, ...] = ()
    required_controls: tuple[str, ...] = ()
    rounding_defaults: tuple[TemplateRoundingDefault, ...] = ()
    external_link_policy: ExternalLinkPolicy = ExternalLinkPolicy(
        allowed_states=frozenset({ExternalLinkState.NONE})
    )
    allow_extra_sheets: bool = False
    source_sheet_state_sha256: str | None = None
    source_formula_checkpoint_sha256: str | None = None

    def __post_init__(self) -> None:
        if not self.profile_id.strip():
            raise ValueError("profile_id must not be blank")
        if not self.profile_version.strip():
            raise ValueError("profile_version must not be blank")
        if not self.source_exemplar.strip():
            raise ValueError("source_exemplar must not be blank")
        if not self.required_sheets:
            raise ValueError("profile must declare required sheets")
        if not self.formula_signatures:
            raise ValueError("profile must declare formula signatures")

        sheet_names = [item.name for item in self.required_sheets]
        if len(set(sheet_names)) != len(sheet_names):
            raise ValueError("required sheet names must be unique")

        formula_cells = [item.cell for item in self.formula_signatures]
        if len(set(formula_cells)) != len(formula_cells):
            raise ValueError("formula signature cells must be unique")

        rule_cells = [item.cell for item in self.cell_rules]
        if len(set(rule_cells)) != len(rule_cells):
            raise ValueError("cell-rule cells must be unique")

        transformation_ids = [
            item.transformation_id for item in self.compatibility_transformations
        ]
        if len(set(transformation_ids)) != len(transformation_ids):
            raise ValueError("transformation ids must be unique")

        if len(set(self.required_controls)) != len(self.required_controls):
            raise ValueError("required controls must be unique")

        rounding_targets = [item.target for item in self.rounding_defaults]
        if len(set(rounding_targets)) != len(rounding_targets):
            raise ValueError("rounding-default targets must be unique")

        for value in (
            self.source_sheet_state_sha256,
            self.source_formula_checkpoint_sha256,
        ):
            if value is not None:
                if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                    raise ValueError("source SHA-256 must be lowercase 64-char hex")

    def cell_class_for(self, cell: str) -> CellClass:
        for rule in self.cell_rules:
            if rule.cell == cell:
                return rule.cell_class
        if any(signature.cell == cell for signature in self.formula_signatures):
            return CellClass.OUTPUT_CHECKPOINT
        return CellClass.UNKNOWN

    def formula_alternatives_for(self, cell: str) -> tuple[str, ...]:
        alternatives: list[str] = []
        for transformation in self.compatibility_transformations:
            alternatives.extend(
                item.formula
                for item in transformation.accepted_formula_alternatives
                if item.cell == cell
            )
        return tuple(alternatives)

    def rounding_default_for(self, target: str) -> TemplateRoundingDefault | None:
        for default in self.rounding_defaults:
            if default.target == target:
                return default
        return None
