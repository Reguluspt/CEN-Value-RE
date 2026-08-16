# E0-PR-007 — Encrypted RE Persistence Foundation Implementation Report v1

**Date:** 2026-08-16
**Repository:** `Reguluspt/CEN-Value-RE`
**Branch:** `agent/e0-pr-007-encrypted-persistence`
**Implementation baseline:** `e57e492d59d0160e5f8721d35e8ed21867458f63`
**Final runtime-tested HEAD:** `af74ee3a61302af5b89d1d09a1104b3a1d9a6cf4`
**Binding GitHub Actions run:** `31960660908`
**Runner:** `windows-latest`
**Runtime:** Python `3.11.9`, Flask `3.1.1`, `sqlcipher3 0.6.2`, SQLCipher `4.12.0 community`
**Focused + foundation result:** `131 passed in 2.10s`

## 1. Scope implemented

E0-PR-007 implements only the Epic 0 encrypted persistence foundation:

- a separate canonical RE database path (`cenvalue-re.db`);
- mandatory SQLCipher-backed DB-API adapter with no plaintext SQLite fallback;
- explicit ordered schema migrations and migration-version table;
- framework-independent repository ports for Case, Subject, Comparable, Construction, Adjustment and Approval;
- concrete SQLCipher repository implementations;
- archive/soft-delete baseline for all six repository contracts;
- random 256-bit application master-key lifecycle;
- Windows current-user DPAPI key protection adapter;
- focused acceptance tests and Windows runtime evidence.

It does not implement document-vault encryption, backup/recovery, legacy case import, full later-epic schema coverage, appraisal/business APIs, valuation formulas, Excel runtime or UI features.

## 2. Architecture boundary

Persistence abstractions remain under `src/re/ports/persistence.py` and contain no SQLCipher, SQLite, DPAPI or Flask imports.

Concrete infrastructure is confined to `src/re/adapters/persistence/`.

The existing architecture/import regressions are included in the binding Windows run.

## 3. Separate canonical database

`PersistencePaths` resolves the canonical database to:

`cenvalue-re.db`

under an RE-owned app-data directory.

If a caller configures the canonical RE path to the same resolved file as legacy `cases.db`, `EncryptedREPersistence` rejects construction.

The E0-PR-007 adapter does not open, query, migrate or reshape the legacy database.

Binding tests create a legacy sentinel `cases.db`, hash it before RE open/migration, and prove the hash is unchanged afterwards.

## 4. SQLCipher fail-closed binding

`requirements-re.txt` pins:

`sqlcipher3==0.6.2`

The adapter lazy-loads `sqlcipher3.dbapi2`. There is no `sqlite3` production fallback.

Connection open requires exactly 32 bytes of raw master-key material and performs, in order:

1. `PRAGMA key` with a 256-bit raw hex key;
2. `PRAGMA cipher_version` verification;
3. immediate schema-page read through `sqlite_master` so a wrong key fails during open;
4. foreign-key enablement;
5. WAL mode.

A DB-API connection that behaves like standard SQLite and returns no SQLCipher version is rejected with `SQLCipherSecurityError`.

The binding Windows runtime reports SQLCipher `4.12.0 community`.

## 5. Encrypted-at-rest proof

Binding Windows evidence proves:

- main database header is not `SQLite format 3\0`;
- a sensitive sample client string is absent from raw main DB bytes;
- the live WAL file exists while the encrypted connection is open;
- the sensitive sample string is absent from raw WAL bytes;
- standard Python `sqlite3` cannot query the canonical encrypted DB;
- a random incorrect SQLCipher key is rejected;
- injecting standard `sqlite3` as the DB-API binding is rejected rather than silently degrading to plaintext.

This is runtime evidence against an actual file, not only a mocked encryption contract.

## 6. Master-key lifecycle

For a new RE app-data store:

- `secrets.token_bytes(32)` generates the 256-bit master key;
- the key protector wraps it before persistence;
- only a versioned wrapped blob is written to `cenvalue-re.masterkey`;
- subsequent opens unwrap and reuse the same master key rather than generating a replacement;
- the raw master key is not written into the wrapped-key file.

The key file is created via an exclusive temporary file, flushed/fsynced and atomically replaced into the final path. A restrictive file mode is applied where the OS supports it.

Unknown wrapped-key file formats fail closed.

## 7. Windows DPAPI production baseline

`WindowsDPAPIKeyProtector` uses Windows `CryptProtectData` / `CryptUnprotectData` through `ctypes`.

The implementation:

- is available only on Windows;
- declares production scope `CURRENT_USER`;
- does not use `CRYPTPROTECT_LOCAL_MACHINE`;
- uses `CRYPTPROTECT_UI_FORBIDDEN` for noninteractive operation;
- passes no optional entropy or prompt structure;
- frees DPAPI-allocated output/description memory via `LocalFree`.

Two levels of proof are included:

1. a fake Win32 ABI test checks flags, protect/unprotect call flow and `LocalFree` behavior;
2. the binding `windows-latest` run executes a real `CryptProtectData` / `CryptUnprotectData` round-trip and a real wrapped-key-file lifecycle.

The binding vector records `dpapi_real_round_trip=true`.

## 8. Explicit transactional migrations

Schema versioning uses `re_schema_migration`.

Migration v1 is explicit ordered Python data and creates the Epic 0 foundation tables:

- `appraisal_case`;
- `property`;
- `subject_property`;
- `comparable_property`;
- `construction_asset`;
- `adjustment_decision`;
- `approval_submission`.

Each unapplied migration executes inside `BEGIN IMMEDIATE`, applies statements in order, records its version only after all statements succeed, and commits at the end.

On error, the transaction rolls back. A deliberate migration failure test confirms its created table is absent afterwards and schema version remains at the last successful migration.

Unknown/future migration versions fail closed.

There is no runtime `ALTER TABLE` loop as the primary migration model.

## 9. Exact numeric persistence

Money, decimal and percentage persistence fields that must preserve textual scale are stored as `TEXT` at this foundation boundary.

Repository acceptance tests round-trip exact values such as:

- `6500000.00`;
- `0.8750`;
- `0.0000`;
- `1706250000.000000`.

No binary-float conversion is introduced by the persistence adapter.

## 10. Repository contracts

Framework-independent ports and SQLCipher implementations are provided for exactly six Epic 0 repository areas:

1. Case;
2. Subject Property;
3. Comparable Property;
4. Construction Asset;
5. Adjustment Decision;
6. Approval Submission.

Binding tests prove create/update/read round trips for all six.

Archive/soft-delete is also exposed and proven for all six contracts. Archiving sets `archived_at` rather than issuing destructive deletes.

## 11. Verification history

Three verification runs occurred. Only the final Windows run is binding evidence.

### Run 1 — `31960133547`

Ubuntu verification succeeded with `129 passed in 1.08s` and actual SQLCipher evidence.

It was deliberately superseded before review because pre-review self-audit found that the explicit soft-delete/archive baseline should be exposed for all six repository ports, not only Case, and DPAPI deserved stronger call-path proof.

Its evidence was removed from the current tree before the corrective implementation was rerun.

### Run 2 — `31960466426`

Ubuntu verification succeeded with `130 passed in 1.65s` after six-repository archive closure and fake Win32 DPAPI ABI proof.

It was deliberately superseded before review to upgrade qualification to the Windows target platform and add live WAL plaintext inspection plus real DPAPI execution.

Its evidence was removed from the current tree before the final target-platform run.

### Run 3 — `31960660908` — BINDING

Tested HEAD:

`af74ee3a61302af5b89d1d09a1104b3a1d9a6cf4`

Runner:

`windows-latest`

Runtime:

- Python `3.11.9`;
- Flask `3.1.1`;
- `sqlcipher3 0.6.2`;
- SQLCipher `4.12.0 community`.

Result:

`131 passed in 2.10s`.

The final run is the only binding acceptance evidence.

## 12. Binding runtime vectors

The final vector log records:

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

## 13. Evidence files

- `evidence/E0_PR_007_RUNTIME_EVIDENCE_v1.md`
- `evidence/E0-PR-007_tests_v1.log`
- `evidence/E0-PR-007_persistence_vectors_v1.log`
- `evidence/E0_PR_007_INDEPENDENT_REVIEW_HANDOFF_v1.md`
- this implementation report.

## 14. Gate

This report is implementation evidence, not self-acceptance.

E0-PR-007 must remain unmerged and E0-PR-008 must not begin until an independent reviewer returns `ACCEPTED` against the exact review HEAD and confirms the delta after the runtime-tested HEAD contains no untested implementation change.
