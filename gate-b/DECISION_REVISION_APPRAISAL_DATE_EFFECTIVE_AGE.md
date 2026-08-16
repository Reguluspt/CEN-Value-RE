# Decision Revision — Effective Age Reference Date
**Date:** 2026-08-15
**Status:** ĐÃ CHỐT

## Workbook behavior
Legacy workbook sample uses `YEAR(NOW()) - construction_year`.

## New CenValue RE decision
Use the appraisal date stored in `AppraisalCase.appraisal_date`, not the workstation/current date.

`effective_age_years = YEAR(appraisal_date) - construction_year`

The remaining-quality calculation therefore becomes reproducible when a closed case is reopened later.

## Compatibility handling
The Excel output adapter must reproduce the **CenValue canonical result**. It must not allow volatile `NOW()` to change a historical case after export/reopen. Where the legacy template formula uses `NOW()`, the adapter/template profile must neutralize or replace that volatility for the controlled output/checkpoint.

## Provenance
`appraisal_date` is a case-level valuation input and must be included in calculation snapshots and approval submissions.
