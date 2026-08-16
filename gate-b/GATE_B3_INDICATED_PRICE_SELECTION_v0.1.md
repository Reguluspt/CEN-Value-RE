# Gate B.3 — Indicated Price Selection Contract v0.1
**Status:** WORKBOOK-DERIVED + USER RULE RECONCILED


> **SUPERSEDED STATUS NOTE — 2026-08-16**  
> This v0.1 file is retained for provenance. The adjustment-amplitude blocker and 15% readiness behavior were resolved later in Gate B and are closed for the Walking Skeleton. Use the latest Gate B closure/checkpoint contracts as current authority; the “Remaining blocker” section below is historical.

## Metrics traced from Sheet1
For each comparable:
- adjustment count: counts non-zero adjustment decisions;
- gross adjustment value: sum of absolute adjustment amounts;
- net adjustment value: signed sum of adjustment amounts;
- adjustment amplitude: derived from the absolute adjustment-rate set (array formula in workbook; exact formula serialization requires separate extraction).

## Primary selection behavior
The workbook marks the comparable(s) whose gross adjustment value is the minimum.

If exactly one comparable has the minimum gross adjustment, its indicated unit price is selected.

If two or three comparables have zero/equal-minimum behavior, workbook contains special branches that may use the average of their indicated prices.

This aligns with the approved narrative that selection considers:
- gross adjustment;
- adjustment count;
- adjustment amplitude;
- net adjustment;
- information quality;
while giving priority to the smallest gross adjustment where information quality supports the choice.

## CenValue RE design
Do not encode the workbook's text-concatenation branches as domain logic.

Create a deterministic `ComparableQualityMetrics` set and a `GuidanceCandidate` result:
- comparable_id
- indicated_unit_price
- gross_adjustment_value
- adjustment_count
- adjustment_amplitude
- net_adjustment_value
- information_quality
- is_min_gross_adjustment
- recommendation_reason

System recommendation is advisory.
Human appraiser confirms:
- selected comparable, or
- selected average/other supported indication.

The final decision and reason snapshot are persisted for audit.

## Special equality behavior
Averages must only be automatically proposed when the applicable candidates satisfy the frozen equality/tie rule. The appraiser remains able to select the final indicated price.

## Validation
The workbook narrative includes a 15% control around the average indicated prices. CenValue RE will expose this as a readiness/quality validation, not silently modify adjustment rates.

## Remaining blocker
Extract the exact legacy array formula for adjustment amplitude and test it against sample workbook values before freezing the compatibility formula.
