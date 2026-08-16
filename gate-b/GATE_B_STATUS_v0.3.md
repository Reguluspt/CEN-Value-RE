# Gate B — Closure Status v0.3

## Design decisions now frozen
- Canonical calculation source vs Excel compatibility role.
- Appraisal-date-based CTXD effective age.
- CTXD age/expert/average/replacement/remaining-value chain.
- Adjustment C1–C11 registry and additive/base behavior.
- Explicit 0% semantics.
- Comparable quality metrics and adjustment amplitude.
- Indicated-price recommendation/selection model.
- Land + CTXD + total-value calculation chain.
- Separate pre-rounding and rounded final values.
- Configurable case-level RoundingPolicy with template defaults.
- G181/G182 output-consumer distinction.
- stale external self-reference handling.
- template fingerprint/signature strategy.
- dependency classification boundary.
- golden-case checkpoint strategy.
- Microsoft Excel qualification protocol.

## Gate B conclusion
**DESIGN READY / FROZEN FOR WALKING SKELETON.**

The remaining exhaustive legacy-cell inventory is implementation evidence, not a prerequisite for starting the engineering foundation. Unknown dependencies remain fail-safe findings during adapter qualification.

## Next phase
Proceed to **Epic 0 — Engineering Foundation**, then **Epic 1 — Canonical Case + Walking Skeleton**.

Epic 0 must establish:
1. repository/application shell and Astryx integration spike;
2. framework-independent domain package;
3. encrypted local persistence/migrations;
4. Tauri ↔ local service bootstrap/session boundary;
5. calculation decimal/rounding primitives;
6. Excel profile/fingerprint infrastructure;
7. test architecture and golden-fixture harness.

No appraisal feature should be implemented by extending the legacy flat `cases` table.
