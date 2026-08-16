# Gate B.5 — External Link Classification

**Workbook:** N08-0038_Huedtl_MTN_TranNguyenVanDau_UNLOCKED.xlsx
**Status:** CLASSIFIED — COMPATIBILITY TRANSFORMATION REQUIRED

## Finding
The dependency audit found one external workbook reference.

Direct workbook inspection shows:
`Phieu TTTT!E5 = '[1]Nhập liệu'!F9`

The external-link cache currently resolves this to `Tp. HCM`.

The current workbook also has:
`Nhập liệu!F9 = Tp. HCM`

Therefore this external reference is not an intentional external data dependency for the appraisal calculation. It is a stale/self-copy link left from another workbook.

## Downstream impact
`Phieu TTTT!E5` is referenced by:
- `BC-TSSS!E3`
- address/output strings in `Sheet1`
- `Offical!E33`
- QH lookup logic
- PX lookup logic

Although it does not appear to be part of the core adjustment arithmetic, leaving it external creates a fragile workbook dependency and can affect address/planning/reference outputs.

## CenValue compatibility decision
For the supported template profile, classify this link as:
`STALE_EXTERNAL_SELF_REFERENCE`

Approved profile transformation:
- replace logical dependency of `Phieu TTTT!E5` with the canonical locality/province field that maps to the current workbook's `Nhập liệu!F9`;
- generated approval workbook must not rely on the old external workbook path;
- remove/break the stale external-link relationship when producing a clean CenValue output if doing so does not alter other declared checkpoints.

## Verification
A profile test must verify:
1. output `Phieu TTTT!E5` equals the mapped canonical/current template input;
2. QH/PX/Offical/BC-TSSS dependent outputs remain equivalent;
3. no mandatory checkpoint depends on the unavailable external source;
4. generated workbook contains no unresolved external link for this dependency.

This transformation is versioned in the template profile and recorded in output audit metadata.
