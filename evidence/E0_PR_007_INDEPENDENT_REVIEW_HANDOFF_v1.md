# E0-PR-007 — Independent Review Handoff v1

**Date:** 2026-08-16
**Repository:** `Reguluspt/CEN-Value-RE`
**Branch:** `agent/e0-pr-007-encrypted-persistence`
**Implementation baseline:** `e57e492d59d0160e5f8721d35e8ed21867458f63`
**Runtime-tested HEAD:** `af74ee3a61302af5b89d1d09a1104b3a1d9a6cf4`
**Binding GitHub Actions run:** `31960660908`
**Binding runner:** `windows-latest`
**Runtime:** Python `3.11.9`, Flask `3.1.1`, `sqlcipher3 0.6.2`, SQLCipher `4.12.0 community`
**Result:** `131 passed in 2.10s`
**Decision requested:** `ACCEPTED` / `RETURN FINDINGS`

## Exact review-head rule

Before issuing a verdict, resolve the current PR HEAD directly from GitHub.

If it differs from the exact review HEAD supplied with the PR/review request, stop and report `HEAD MISMATCH` until the delta is reviewed.

The final runtime-tested implementation HEAD is:

`af74ee3a61302af5b89d1d09a1104b3a1d9a6cf4`

Any delta after this commit may contain only:

- successful final-run evidence/logs;
- removal of the one-time verification workflow;
- implementation report;
- independent-review handoff/documentation.

If source, tests, dependency pin, persistence contract or migrations changed after the tested HEAD without another full Windows run, do not accept.

## Frozen authority

Review against:

- `epic-0/EPIC_0_PR_PLAN_v1.md` — E0-PR-007 scope and acceptance;
- `epic-0/EPIC_0_ACCEPTANCE_MATRIX_v1.md`;
- `epic-0/EPIC_0_ENGINEERING_FOUNDATION_PACKET_v1.md`;
- `gate-a/GATE_A3_CANONICAL_SCHEMA_V1.md`;
- `gate-a/GATE_A4_PERSISTENCE_SECURITY_BASELINE.md`;
- `Design Book/15_SECURITY_AND_PRIVACY.md`;
- `epic-0/E0_PR_007_PERSISTENCE_CONTRACT_v1.md`.

## Expected implementation surface

Implementation-bearing files are limited to:

- `requirements-re.txt`;
- `src/re/ports/persistence.py`;
- `src/re/adapters/persistence/__init__.py`;
- `src/re/adapters/persistence/key_protection.py`;
- `src/re/adapters/persistence/migrations.py`;
- `src/re/adapters/persistence/repositories.py`;
- `src/re/adapters/persistence/sqlcipher.py`;
- `src/re/adapters/persistence/store.py`;
- `tests/re/test_encrypted_persistence.py`;
- `epic-0/E0_PR_007_PERSISTENCE_CONTRACT_v1.md`;
- evidence/report files.

The one-time verification workflow must be absent from the final review tree.

## Required technical review

### 1. Scope / architecture

Confirm:

- repository ports remain framework/infrastructure independent;
- Domain/Application do not import SQLCipher, SQLite, ctypes DPAPI or concrete persistence adapters;
- concrete DB/key infrastructure is confined to adapters;
- no appraisal formula/business API is introduced;
- no Excel runtime/fill/recalculation is introduced;
- no UI feature is introduced;
- no document-vault encryption, backup/recovery or legacy import is falsely claimed complete;
- the canonical RE database remains separate from legacy `cases.db`.

Do not fail E0-PR-007 merely because full later-epic schema, document vault, backup/recovery and legacy import are deferred; do fail it if source/report claims those deferred areas are complete.

### 2. SQLCipher fail-closed binding

Confirm `requirements-re.txt` pins:

`sqlcipher3==0.6.2`

Review `src/re/adapters/persistence/sqlcipher.py` and confirm:

- no production fallback to standard `sqlite3`;
- exactly 32-byte raw key required;
- key is supplied before first database operation;
- raw-key syntax is SQLCipher 256-bit hex blob form;
- `PRAGMA cipher_version` is required and empty/non-SQLCipher result rejects;
- a schema-page read occurs after keying so an incorrect key fails during open;
- foreign keys are enabled;
- WAL is enabled;
- a plain SQLite DB-API injected into the opener is rejected rather than accepted silently.

Binding Windows proof must establish:

- SQLCipher runtime is `4.12.0 community`;
- ordinary SQLite header is absent;
- sensitive sample plaintext is absent from main database bytes;
- a live WAL file exists and the same sensitive plaintext is absent from WAL bytes;
- standard Python `sqlite3` cannot query the encrypted database;
- wrong SQLCipher key is rejected.

### 3. Master-key generation and persistence

Confirm:

- new master key is generated with `secrets.token_bytes(32)` or equivalent 256-bit CSPRNG;
- raw master key is never persisted to source, `.env`, DB, normal log or key file;
- only a versioned wrapped-key blob is stored in `cenvalue-re.masterkey`;
- existing wrapped key is unwrapped/reused instead of silently rotating;
- unknown key-file format fails closed;
- key file creation is bounded/atomic rather than direct partially-written replacement.

Independent mutation/probe should confirm the raw master key bytes are not a substring of the persisted wrapped-key file.

### 4. Windows DPAPI user-scope adapter

Review `WindowsDPAPIKeyProtector` carefully.

Required:

- Windows-only production adapter;
- `scope = CURRENT_USER`;
- `CryptProtectData` / `CryptUnprotectData` signatures match Win32 `DATA_BLOB` usage;
- `CRYPTPROTECT_UI_FORBIDDEN` used for noninteractive operation;
- `CRYPTPROTECT_LOCAL_MACHINE` is not used;
- no prompt struct or optional entropy is accidentally required;
- DPAPI-allocated output buffer is released with `LocalFree`;
- unprotected description, when returned, is released with `LocalFree`;
- failures raise a closed error rather than returning input/plaintext.

Binding Windows run must contain a real DPAPI protect/unprotect round-trip, not only a mock.

Expected final vector:

`dpapi_scope=CURRENT_USER`

`dpapi_real_round_trip=true`

A fake Win32 ABI unit test also exercises flags/call flow/free behavior; treat it as supplementary to the real Windows run.

### 5. Migration/versioning review

Review `src/re/adapters/persistence/migrations.py`.

Confirm:

- explicit ordered migration definitions;
- version/name metadata;
- `re_schema_migration` tracks applied versions;
- schema v1 creates the intended foundation tables only;
- each unapplied migration runs in an explicit transaction (`BEGIN IMMEDIATE` or equivalent);
- migration version is recorded only after its statements succeed;
- failure rolls back the migration;
- unknown/future applied migration versions fail closed;
- no runtime `ALTER TABLE` loop is the primary migration mechanism.

Independently inspect the deliberate failing-migration test: the partial table must not survive and applied versions must remain at the last successful version.

### 6. Repository contract review

Confirm framework-independent ports and SQLCipher implementations exist for exactly these six Epic 0 areas:

1. Case;
2. Subject Property;
3. Comparable Property;
4. Construction Asset;
5. Adjustment Decision;
6. Approval Submission.

Round-trip tests must cover all six.

Exact monetary/decimal/percentage strings must preserve textual value/scale and must not pass through binary float. Review vectors such as:

- `6500000.00`;
- `0.8750`;
- `0.0000`;
- `1706250000.000000`.

### 7. Archive / soft-delete baseline

All six repository contracts must expose an archive path and persist `archived_at` rather than issuing destructive delete.

Confirm archive behavior independently for:

- Case;
- Subject;
- Comparable;
- Construction;
- Adjustment;
- Approval.

Subject/Comparable archive metadata lives on the canonical `property` row; other aggregates use their own foundation table.

Do not interpret archive as Historical Learning inclusion/exclusion; that policy is separate.

### 8. Legacy safety

Confirm:

- canonical DB filename/path is distinct from legacy `cases.db`;
- configuring both to the same resolved path is rejected;
- E0-PR-007 does not open/migrate/reshape legacy schema;
- binding test writes a legacy sentinel and confirms byte/hash identity before and after RE open/migration.

Expected vector:

`legacy_hash_unchanged=true`

`same_path_legacy_rejected=true`

### 9. Runtime / regression review

Only this run is binding:

`31960660908`

Expected checked-out/tested HEAD:

`af74ee3a61302af5b89d1d09a1104b3a1d9a6cf4`

Expected runner/runtime:

- `windows-latest`;
- Python `3.11.9`;
- Flask `3.1.1`;
- `sqlcipher3 0.6.2`;
- SQLCipher `4.12.0 community`.

Expected result:

`131 passed in 2.10s`

The run must include:

- architecture/import regressions;
- E0-PR-003 Decimal/RoundingPolicy regressions;
- E0-PR-004 ExcelTemplateProfile/Fingerprint regressions;
- E0-PR-005 Golden Fixture regressions;
- E0-PR-006 Local Service regressions;
- E0-PR-007 encrypted persistence tests;
- target-platform SQLCipher/DPAPI/WAL vectors.

Expected final vector log:

```text
runner_platform=windows
database_name=cenvalue-re.db
schema_version=1
sqlcipher_version=4.12.0 community
wal_present=true
wal_sensitive_plaintext_visible=false
sqlite_plain_header=false
sensitive_plaintext_visible=false
master_key_visible_in_wrapped_file=false
standard_sqlite_queryable=false
wrong_key_rejected=true
plain_sqlite_binding_rejected=true
protected_key_reused=true
repository_count=6
legacy_hash_unchanged=true
same_path_legacy_rejected=true
dpapi_scope=CURRENT_USER
dpapi_real_round_trip=true
```

### 10. Verification-history interpretation

Earlier runs are intentionally non-binding:

- `31960133547`: Ubuntu, `129 passed`; superseded by six-repository archive closure and stronger DPAPI proof;
- `31960466426`: Ubuntu, `130 passed`; superseded by target-platform Windows qualification and WAL inspection;
- `31960660908`: Windows, `131 passed`; final binding run.

Do not use run 1 or run 2 as substitute acceptance evidence for the final implementation.

### 11. Evidence binding

Compare the runtime-tested HEAD to the exact current PR review HEAD.

The post-test delta may contain only:

- final successful evidence/logs;
- removal of the one-time workflow;
- implementation report;
- independent-review handoff/documentation.

There must be no untested post-run change to:

- `requirements-re.txt`;
- `src/re/ports/persistence.py`;
- `src/re/adapters/persistence/*`;
- `tests/re/test_encrypted_persistence.py`;
- `epic-0/E0_PR_007_PERSISTENCE_CONTRACT_v1.md`.

If any such implementation-bearing file changed after `af74ee3a61302af5b89d1d09a1104b3a1d9a6cf4`, do not accept without a new binding Windows run.

## Primary evidence

- `evidence/E0_PR_007_RUNTIME_EVIDENCE_v1.md`
- `evidence/E0-PR-007_tests_v1.log`
- `evidence/E0-PR-007_persistence_vectors_v1.log`
- `implementation/E0_PR_007_IMPLEMENTATION_REPORT_v1.md`
- this handoff.

## Finding format

For each finding report:

- ID;
- severity: BLOCKER / HIGH / MEDIUM / LOW;
- exact file/path;
- exact issue;
- why it matters;
- required corrective action;
- acceptance test for closure.

Do not create blocking findings for cosmetic/style preference.

## Required verdict

If clean:

```text
FINDINGS
- NONE

VERDICT:
ACCEPTED

E0-PR-007 may proceed to merge and E0-PR-008 may begin after merge.
```

If findings exist:

```text
VERDICT:
RETURN FINDINGS

OPEN FINDINGS:
- ...

E0-PR-007 must not merge and E0-PR-008 must not begin until findings are closed.
```

E0-PR-007 is not self-accepted by the implementer.
