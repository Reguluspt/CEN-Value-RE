# E1-PR-006 — Local Service + Astryx Manual Workbench Integration Contract v1

**Status:** IMPLEMENTATION CONTRACT — EPIC 1
**Accepted base:** `be537e573d6692c6cbfaf5a6cb3710ad7c229177`
**Gate:** `ManualWorkbenchGate`

## 1. Purpose and authority

E1-PR-006 exposes the already accepted Epic 1 manual Walking Skeleton through the loopback local-service boundary and the isolated Astryx `/re` workbench.

The authoritative sequence remains:

`Create Case → TSTĐ → TSSS01/02/03 → C1–C11 → Quality → Human Indication → Final Valuation → Workbook Export`

This PR consumes accepted E1-PR-001 through E1-PR-005 application contracts. It does not redefine their formulas, currentness rules, evidence bindings, rounding semantics, workbook write authority, or Excel qualification boundary.

Historical Brainstorm/Design Book material is provenance only where later accepted contracts are stronger.

## 2. Architecture boundary

- React/Astryx is presentation only.
- Flask local-service routes are transport adapters only.
- Business calculation and currentness remain in `src/re/application` and `src/re/domain`.
- Frontend code must not import persistence, Excel-output adapter, SQLCipher, or Python implementation internals.
- Local-service route modules must not execute valuation formulas or query SQL directly.
- Existing application services remain the calculation/currentness authority.

No frontend result may be computed by duplicating a valuation formula already owned by the application layer.

## 3. Local-service security and bootstrap

All E1-PR-006 HTTP routes remain under `/api/re` and inherit the E0-PR-006 loopback/session guard.

Every request requires the current launch ID and bearer token. There is no anonymous RE route, no HTTP bootstrap route, no persisted credential file, and no fixed credential fallback.

The workbench API client is constructed from an in-memory bootstrap envelope supplied by the desktop/supervisor boundary:

- `base_url`;
- `launch_id`;
- `bearer_token`.

The concrete Tauri IPC/sidecar delivery mechanism remains outside this PR. Tests may inject the envelope explicitly in memory; production/browser code must fail closed when it is absent.

Error payloads preserve the structured local-service envelope and never include the bearer token.

## 4. HTTP capability surface

Existing E1-PR-001 routes remain authoritative and unchanged in meaning:

- `POST /api/re/manual-cases`;
- `GET /api/re/manual-cases/<case_id>`;
- `PUT /api/re/manual-cases/<case_id>/subject`;
- `PUT /api/re/manual-cases/<case_id>/comparables/<1|2|3>`.

E1-PR-006 adds bounded transport routes over accepted application services for:

### Adjustment

- bind/read current normalized adjustment source state per comparable;
- explicitly select one C1–C11 rate with human actor metadata;
- read current explicit decisions, including explicit zero distinct from missing;
- run the accepted E1-PR-002 adjustment calculation;
- return persisted application result/snapshot metadata, not a frontend recomputation.

### Quality and human indication

- read E1-PR-003 current comparable quality/readiness/guidance preview;
- explicitly confirm the human indication;
- read the current confirmation when still valid;
- system guidance may populate a candidate but may never auto-submit the confirmation.

### Final valuation

- bind the typed `SUPPLIED_PRECOMPUTED` construction aggregate boundary input;
- compose the E1-PR-004 final valuation;
- read only a current final valuation snapshot;
- stale upstream evidence fails closed and requires recomposition/reconfirmation as defined upstream.

### Workbook export

- request E1-PR-005 supported-profile workbook generation using case identity plus explicit template/output paths;
- return artifact SHA/binding/generation metadata from the application/writer contract;
- export is blocked when current final/canonical prerequisites fail;
- successful generation remains `excel_qualification_status = NOT_RUN`.

Route names may be adapter-facing, but each route must map one-to-one to an accepted application use case or a bounded read model. No route may introduce a second calculation implementation.

## 5. Rounding authority at the HTTP boundary

For the supported N08 profile, the browser does not submit or calculate trusted template-default increments.

When the user chooses template-default rounding, the adapter/application composition resolves the accepted `ExcelTemplateProfile` default and constructs the trusted `RoundingPolicy` server-side.

A case override remains explicit and must preserve the accepted actor/time audit metadata and existing validation rules.

The frontend must never hard-code `1,000 VND/m²` or `1,000,000 VND` as calculation authority.

## 6. Percentage display/input boundary

Canonical selected adjustment rates remain fractional decimal strings:

`5% -> "0.05"`

The browser may display percentage points but must convert text to/from canonical fraction representation at the UI adapter boundary without binary floating-point calculation.

Required semantics:

- blank/unentered stays missing;
- explicit `0` becomes canonical `"0"` and remains visibly entered;
- `5` display percent becomes canonical `"0.05"`;
- `-5` becomes `"-0.05"`;
- malformed/non-finite values reject before submission.

The UI may not substitute missing with zero.

## 7. Workbench resume/read model

Reload/resume must reconstruct presentation state from persisted/application evidence rather than browser-local calculation state.

At minimum the workbench can recover:

- manual case/profile/appraisal date;
- current subject and TSSS01/02/03 input data;
- per-comparable current C1–C11 selections/review status/source revision;
- latest/current adjustment result when valid;
- current quality/readiness/guidance preview when prerequisites are complete;
- current human indication when still valid;
- current final valuation when still valid.

Incomplete or stale later-stage evidence is represented as unavailable/blocked, not fabricated. Earlier persisted manual inputs remain resumable.

## 8. Astryx `/re` workbench

The existing isolated `/re` route remains admin-protected and outside the legacy Ant Design `Layout`.

The spike surface is replaced by a bounded manual workbench with visible stages for:

1. case create/resume;
2. TSTĐ;
3. TSSS01/02/03;
4. C1–C11 human selections and adjustment run;
5. quality/readiness;
6. human indication confirmation;
7. final valuation;
8. workbook export.

The workbench must:

- present canonical application errors without exposing secrets;
- visibly distinguish missing and explicit zero decisions;
- require explicit human clicks for selected-rate and indication decisions;
- render results returned by application/local-service responses;
- remain usable for the core manual flow without OCR, Maps, AI, or external network providers.

## 9. CSS and legacy non-regression

The accepted E0 Astryx isolation remains mandatory:

- scoped Astryx vendor CSS only inside `.cenvalue-re-surface`;
- no `:root`, `html[data-theme]`, global `body`, or document-root token mutation from the RE surface;
- legacy `/dashboard` and `/cases` computed-style non-regression remains covered;
- generated scoped vendor CSS remains reproducible and untracked as previously accepted.

E1-PR-006 may extend authored RE styles but may not weaken the existing isolation verifier.

## 10. Negative behavior

E1-PR-006 must fail closed when:

- local-service bootstrap/session credentials are absent, stale, invalid, or revoked;
- user is not authorized for `/re`;
- mandatory C1–C11 decisions are incomplete/stale when attempting downstream calculation;
- human indication has not been explicitly confirmed;
- final valuation prerequisites are missing/stale;
- workbook source/profile/current canonical evidence is unsupported or stale.

A disabled UI control is not sufficient proof by itself; the corresponding local-service/application call must also reject invalid state.

## 11. Acceptance proof

Binding evidence must include:

- browser-level vertical smoke through the manual path to a workbook-generation request;
- reload/resume proof that persisted inputs and explicit decisions are restored;
- explicit-zero versus missing UI/API proof;
- percentage conversion unit/adapter proof without binary-float semantics;
- structured error rendering proof;
- local-service session negative vectors remain green;
- existing Astryx CSS/document-root negative controls remain green;
- no frontend import of persistence/Excel adapter internals;
- full accepted Python RE regression;
- scoped/new frontend lint plus inherited full-lint non-regression;
- production frontend build.

`ManualWorkbenchGate = PASS` does not imply Microsoft Excel Desktop qualification PASS and does not close Epic 1.

## 12. Explicit non-scope

Not implemented or claimed here:

- E1-PR-007 real Microsoft Excel Desktop full-recalculation qualification;
- Epic 1 closure;
- approval return/revision import;
- generic workbook-family rewriting or external-link repair;
- Epic 2 CTXD engine;
- OCR/Maps/provider automation;
- Historical Learning / AI suggestion engine;
- concrete production Tauri IPC/sidecar credential transport beyond the accepted in-memory boundary.