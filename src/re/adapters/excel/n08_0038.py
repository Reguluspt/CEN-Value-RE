"""Frozen N08-0038 ExcelTemplateProfile data for E0-PR-004."""

from __future__ import annotations

from .profile import (
    CellClass,
    CellRule,
    CompatibilityTransformation,
    ExcelTemplateProfile,
    ExternalLinkPolicy,
    ExternalLinkState,
    FormulaSignature,
    SheetRequirement,
    SheetState,
    TemplateRoundingDefault,
)


_N08_SHEETS = (
    SheetRequirement("Hồ sơ", SheetState.VISIBLE),
    SheetRequirement("Nhập liệu", SheetState.VISIBLE),
    SheetRequirement("Phieu TTTT", SheetState.VISIBLE),
    SheetRequirement("Bangtinh", SheetState.VISIBLE),
    SheetRequirement("Kehoach", SheetState.VISIBLE),
    SheetRequirement("Data", SheetState.VISIBLE),
    SheetRequirement("BC-TSTĐG", SheetState.HIDDEN),
    SheetRequirement("BC-TSSS", SheetState.HIDDEN),
    SheetRequirement("Sheet1", SheetState.HIDDEN),
    SheetRequirement("List", SheetState.HIDDEN),
    SheetRequirement("Offical", SheetState.VISIBLE),
    SheetRequirement("BGD", SheetState.HIDDEN),
    SheetRequirement("TL", SheetState.HIDDEN),
    SheetRequirement("TTp", SheetState.HIDDEN),
    SheetRequirement("QH", SheetState.HIDDEN),
    SheetRequirement("PX", SheetState.HIDDEN),
)

_N08_FORMULAS = (
    FormulaSignature("Bangtinh!F108", "=F107"),
    FormulaSignature("Bangtinh!G108", "=G107"),
    FormulaSignature("Bangtinh!H108", "=H107"),
    FormulaSignature("Bangtinh!F112", "=Sheet1!A22"),
    FormulaSignature("Bangtinh!G112", "=Sheet1!B22"),
    FormulaSignature("Bangtinh!H112", "=Sheet1!C22"),
    FormulaSignature("Bangtinh!H119", "=ROUND(Sheet1!G18,-3)"),
    FormulaSignature("Bangtinh!H127", "=ROUND((E127-F127)/E127+G127,2)"),
    FormulaSignature("Bangtinh!F140", "=ROUND(100%-F139,2)"),
    FormulaSignature("Bangtinh!H153", "=ROUND(($H127+$F140)/2,2)"),
    FormulaSignature("Bangtinh!G156", "=F156*E156*D156"),
    FormulaSignature("Bangtinh!H161", "=F161*D161*G161"),
    FormulaSignature("Bangtinh!H163", "=SUM(H162+H161)"),
    FormulaSignature("Bangtinh!G171", "=F171*E171"),
    FormulaSignature(
        "Bangtinh!G169",
        '=IF(\'Hồ sơ\'!G14="Shinhan",SUBTOTAL(9,G170:G173),SUBTOTAL(9,Bangtinh!G170:G178))',
    ),
    FormulaSignature(
        "Bangtinh!G178",
        '=IF(\'Hồ sơ\'!G14="Shinhan",SUBTOTAL(9,G179),SUBTOTAL(9,Bangtinh!G179:G180))',
    ),
    FormulaSignature("Bangtinh!G181", "=ROUND(G169+G178,0)"),
    FormulaSignature("Bangtinh!G182", "=ROUND(G181,-6)"),
    FormulaSignature(
        "Sheet1!A18",
        '=IF(MIN(IF(A7:A17>0,A7:A17))<>MAX(IF(A7:A17>0,A7:A17)),CONCATENATE(MIN(IF(A7:A17>0,A7:A17))," - ",MAX(IF(A7:A17>0,A7:A17))),MIN(IF(A7:A17>0,A7:A17)))',
    ),
    FormulaSignature("Sheet1!A20", '=(COUNTIF(Bangtinh!F53:F107,"<>0")-33)/2'),
    FormulaSignature(
        "Sheet1!A22",
        "=ABS(Bangtinh!F56)+ABS(Bangtinh!F61)+ABS(Bangtinh!F71)+ABS(Bangtinh!F76)+ABS(Bangtinh!F81)+ABS(Bangtinh!F86)+ABS(Bangtinh!F91)+ABS(Bangtinh!F66)+ABS(Bangtinh!F96)+ABS(Bangtinh!F101)+ABS(Bangtinh!F106)",
    ),
    FormulaSignature(
        "Sheet1!A24",
        '=SUMIF(Bangtinh!$C$53:$C$107,"Mức điều chỉnh",Bangtinh!F$53:F$107)',
    ),
    FormulaSignature(
        "Sheet1!G18",
        '=IF(COUNTIF(Bangtinh!$F$112:$H$112,"0")<2,$G$14,$C$35)',
    ),
    FormulaSignature("Offical!E32", "=Bangtinh!G181"),
)

_N08_CELL_RULES = tuple(
    CellRule(signature.cell, CellClass.OUTPUT_CHECKPOINT)
    for signature in _N08_FORMULAS
) + (
    CellRule("Bangtinh!F127", CellClass.VOLATILE_COMPAT_OVERRIDE),
    CellRule("Phieu TTTT!E5", CellClass.VOLATILE_COMPAT_OVERRIDE),
)

_N08_TRANSFORMATIONS = (
    CompatibilityTransformation(
        transformation_id="effective-age-appraisal-date",
        description=(
            "Replace volatile construction effective-age semantics based on "
            "YEAR(NOW()) with AppraisalCase.appraisal_date."
        ),
        affected_cells=("Bangtinh!F127", "Bangtinh!H127"),
    ),
    CompatibilityTransformation(
        transformation_id="localize-stale-phieu-tttt-e5",
        description=(
            "Replace the stale external self-reference at Phieu TTTT!E5 "
            "with the canonical/template locality value."
        ),
        affected_cells=("Phieu TTTT!E5",),
    ),
)

_N08_ROUNDING_DEFAULTS = (
    TemplateRoundingDefault("UNIT_PRICE", "NEAREST", 1_000),
    TemplateRoundingDefault("TOTAL_VALUE", "NEAREST", 1_000_000),
)


N08_0038_PROFILE = ExcelTemplateProfile(
    profile_id="cenvalue-re-n08-0038-v1",
    profile_version="1",
    source_exemplar="N08-0038_Huedtl_MTN_TranNguyenVanDau_UNLOCKED.xlsx",
    required_sheets=_N08_SHEETS,
    formula_signatures=_N08_FORMULAS,
    cell_rules=_N08_CELL_RULES,
    compatibility_transformations=_N08_TRANSFORMATIONS,
    # Gate-B v1 names no concrete required named/control ranges.  The schema
    # supports them and will fail closed as soon as a profile declares them.
    required_controls=(),
    rounding_defaults=_N08_ROUNDING_DEFAULTS,
    external_link_policy=ExternalLinkPolicy(
        allowed_states=frozenset(
            {
                ExternalLinkState.NONE,
                ExternalLinkState.KNOWN_STALE_SELF_REFERENCE,
            }
        ),
        warning_states=frozenset(
            {ExternalLinkState.KNOWN_STALE_SELF_REFERENCE}
        ),
    ),
    allow_extra_sheets=False,
    source_sheet_state_sha256=(
        "481997e9672fa4fa88a8b00cb677280e72916b5ce29fde0625f508409ab5e951"
    ),
    source_formula_checkpoint_sha256=(
        "05812836786218f2893feeb065e271b515b777aa8b3b5965dcc8c9819a4e2d7d"
    ),
)
