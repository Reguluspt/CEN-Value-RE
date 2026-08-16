# CenValue RE — Gate B.9 Excel Template Fingerprint & Family Contract v0.1

**Date:** 2026-08-15  
**Status:** DESIGN CONTRACT FROZEN; FAMILY CORPUS OPEN

## Purpose

Historical workbooks and approval templates may share appearance while differing in formulas, factors or bank/client-specific branches.

CenValue must identify the template before extracting/filling it.

## Fingerprint dimensions

A TemplateProfile fingerprint uses stable structure, not user data:

1. sheet names + order;
2. sheet visibility;
3. defined-name signatures;
4. key anchor labels;
5. key formula signatures in calculation regions;
6. merged-range/protection signatures where relevant;
7. workbook external-link inventory;
8. optional workbook metadata/version markers.

Do **not** fingerprint by full-file hash because every completed case contains different values.

## Required anchor examples for current sample family

- sheet `Bangtinh`;
- `Bangtinh!C47 = "Yếu tố so sánh"`;
- `Bangtinh!C108 = "Mức giá chỉ dẫn"`;
- `Bangtinh!C112 = "Tổng giá trị điều chỉnh gộp"`;
- `Bangtinh!C165/B165` final-value section anchor;
- CTXD section anchors around rows 123–163;
- formula signature for `Sheet1!F12:H12`;
- formula signature for `Sheet1!A18:C24`;
- formula signature for `Bangtinh!H119`;
- expected sheet set including `Nhập liệu`, `Phieu TTTT`, `Bangtinh`, `Data`, `Sheet1`, etc.

## Match states

```text
EXACT_PROFILE_MATCH
KNOWN_FAMILY_VARIANT
UNKNOWN_TEMPLATE
CORRUPTED_OR_UNSAFE_TEMPLATE
```

Behavior:
- exact/known variant → proceed using declared mappings;
- unknown → do not fill silently; require profiling/mapping;
- corrupted/unsafe → fail closed.

## External links

External-link inventory is part of fingerprint/safety validation.

A known redundant link may have a declared replacement rule.
Any unknown external link blocks verified export until reviewed.

## Template family

A `TemplateFamily` groups profiles with shared business semantics but allows:
- different cell coordinates;
- different bank/client branches;
- added/removed factors;
- altered formulas/rounding.

The domain contract stays stable; mapping/profile version absorbs workbook differences.

## Versioning

Each ApprovalSubmission records:
- template_family_id;
- template_profile_id;
- profile_version;
- workbook structural fingerprint;
- output hash.

Historical Learning also stores the profile/family used for extraction.
