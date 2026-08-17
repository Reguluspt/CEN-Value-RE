"""CenValue RE Excel compatibility adapter infrastructure."""

from .fingerprint import (
    FingerprintIssue,
    FingerprintIssueLevel,
    FingerprintMatchResult,
    FingerprintStatus,
    FormulaObservation,
    SheetObservation,
    UnsupportedTemplateError,
    WorkbookFingerprintObservation,
    formula_signature_digest,
    match_template_profile,
    normalize_formula,
    sheet_state_digest,
)
from .n08_0038 import N08_0038_PROFILE
from .profile import (
    CellClass,
    CellRule,
    CompatibilityTransformation,
    ExcelTemplateProfile,
    ExternalLinkPolicy,
    ExternalLinkState,
    FormulaAlternative,
    FormulaSignature,
    SheetRequirement,
    SheetState,
    TemplateRoundingDefault,
)
from .rounding_defaults import (
    ExcelTemplateRoundingDefaultResolver,
    SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS,
)

__all__ = [
    "CellClass",
    "CellRule",
    "CompatibilityTransformation",
    "ExcelTemplateProfile",
    "ExcelTemplateRoundingDefaultResolver",
    "ExternalLinkPolicy",
    "ExternalLinkState",
    "FingerprintIssue",
    "FingerprintIssueLevel",
    "FingerprintMatchResult",
    "FingerprintStatus",
    "FormulaAlternative",
    "FormulaObservation",
    "FormulaSignature",
    "N08_0038_PROFILE",
    "SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS",
    "SheetObservation",
    "SheetRequirement",
    "SheetState",
    "TemplateRoundingDefault",
    "UnsupportedTemplateError",
    "WorkbookFingerprintObservation",
    "formula_signature_digest",
    "match_template_profile",
    "normalize_formula",
    "sheet_state_digest",
]
