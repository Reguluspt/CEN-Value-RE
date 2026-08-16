# E0-PR-003 — Decimal + RoundingPolicy — Implementation Report v1

**Date:** 2026-08-16
**Status:** IMPLEMENTED; RUNTIME EVIDENCE GREEN; INDEPENDENT ACCEPTANCE PENDING
**Repository:** `Reguluspt/CEN-Value-RE`
**Implementation baseline:** `d89334c4c0ba5a666d4ce5556bc665d6e74750c0`
**Runtime-tested HEAD:** `6e966d174efe0fb3072d20167ebdf636de1c4529`
**Successful GitHub Actions run:** `31953123525`
**Focused suite:** `44 passed in 0.09s`
**Publish status:** FEATURE BRANCH ONLY; NOT MERGED / NOT DEPLOYED

## Frozen scope implemented

E0-PR-003 implements framework-independent numeric and rounding primitives only:

- `Money` backed by `Decimal`;
- `Percentage` backed by canonical fractional `Decimal` (`5% = Decimal("0.05")`);
- `UnitPrice` backed by `Decimal`;
- binary-float rejection at the canonical numeric boundary;
- explicit `RoundingPolicy` with `NEAREST` mode;
- `NONE`, 1k, 10k, 100k, 1m, 10m and arbitrary positive whole-VND custom increments;
- policy resolution priority: case override -> template default -> application default;
- separate immutable raw and rounded values;
- profile/audit metadata fields required by the frozen Gate-B contract;
- open `RoundingTarget` identifier so future profiles can add targets without changing a closed core enum.

No valuation formula engine, Excel adapter/profile implementation, persistence, API/service, UI, OCR/provider, or Epic 1 feature is introduced.

## Implementation files

- `src/re/domain/common/numeric.py`
- `src/re/domain/common/rounding.py`
- `src/re/domain/common/__init__.py`

Tests:

- `tests/re/test_numeric_primitives.py`
- `tests/re/test_rounding_policy.py`

Evidence:

- `evidence/E0_PR_003_RUNTIME_EVIDENCE_v1.md`
- `evidence/E0-PR-003_tests_v1.log`

## Numeric boundary

`DecimalInput` accepts only:

- `Decimal`;
- `int` (excluding `bool`);
- exact decimal strings.

Binary `float` is rejected rather than converted. Non-finite decimal values (`NaN`, `Infinity`) are rejected. The focused tests include an AST guard that fails if a binary-float literal or `float()` conversion is introduced into the numeric/rounding implementation modules.

The value objects preserve exact decimal precision and do not silently quantize at construction. Rounding happens only through an explicit `RoundingPolicy` checkpoint.

## Rounding behavior

`increment_vnd=None` represents `NONE`. Any explicit increment must be a positive whole-VND integer.

Nearest-increment rounding uses Python `Decimal` with `ROUND_HALF_UP`. For signed values this gives the Excel-compatible midpoint behavior required by the frozen contract: half values round away from zero (for example `1500 -> 2000` and `-1500 -> -2000` at a 1,000 VND increment).

The operation uses a local Decimal context sized from the input and increment so the result does not depend on an ambient/global Decimal precision setting.

`RoundingResult` binds:

- the effective policy;
- `raw_value`;
- `rounded_value`.

The raw value is never overwritten.

## Resolution behavior

`resolve_rounding_policy()` resolves:

1. explicit case override;
2. template/profile default;
3. application default.

The resolver fails closed if a candidate has the wrong target or source classification, or if no effective policy exists.

An explicit case override with `increment_vnd=None` is a real `NONE` decision and is not treated as a missing override.

Case overrides require `selected_by` and `selected_at`, preserving the frozen audit boundary. AI-driven silent policy changes are not introduced.

## Frozen N08 compatibility vectors

N08-0038 template defaults are represented through policy instances, not hard-coded global behavior:

- UNIT_PRICE default 1,000 VND: `196,308,350 -> 196,308,000`;
- TOTAL_VALUE default 1,000,000 VND: `19,581,412,440 -> 19,581,000,000`.

Both vectors pass in the runtime evidence suite.

## Verification

GitHub Actions run `31953123525` checked out exact HEAD `6e966d174efe0fb3072d20167ebdf636de1c4529` with Python 3.11.15.

The workflow established:

- domain-common compile: PASS;
- bounded-scope guard: PASS;
- `git diff --check`: PASS;
- existing RE architecture/import regression tests: PASS;
- numeric + rounding tests: PASS;
- total focused result: **44 passed in 0.09s**.

The first workflow attempt was stopped before pytest by trailing whitespace inside the temporary workflow file itself. That harness-only formatting issue was corrected; it did not modify E0-PR-003 implementation source. Only run `31953123525` is the successful runtime evidence source.

## Acceptance status

**NOT SELF-ACCEPTED.** E0-PR-003 requires independent review against the exact final PR head. E0-PR-004 must not begin until E0-PR-003 is independently accepted and merged.
