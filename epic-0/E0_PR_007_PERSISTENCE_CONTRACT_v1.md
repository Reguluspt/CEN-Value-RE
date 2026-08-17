# E0-PR-007 — Encrypted RE Persistence Contract v1

**Baseline:** `e57e492d59d0160e5f8721d35e8ed21867458f63`
**Scope:** Epic 0 persistence foundation only.

## Canonical database boundary

- The RE database is `cenvalue-re.db` under an RE-owned app-data directory.
- It is separate from legacy `cases.db`; pointing both paths at the same file is rejected.
- Legacy storage is not migrated, altered, or queried by this adapter.
- SQLCipher is mandatory. Standard/plain SQLite is not an allowed fallback.

## Encryption binding

- Python binding: `sqlcipher3==0.6.2`.
- The database receives a 256-bit random raw key.
- Runtime verifies `PRAGMA cipher_version` before migrations or repository access.
- Existing encrypted databases are forced through an immediate schema-page read so a wrong key fails during open.
- CI acceptance must verify the database does not carry the ordinary `SQLite format 3\0` plaintext header and cannot be queried by standard `sqlite3`.

The exact installer/distribution packaging remains a pre-pilot concern under Gate A.4; this PR freezes the application adapter contract and a concrete tested SQLCipher binding.

## Master-key protection

Production Windows baseline:

1. Generate `secrets.token_bytes(32)` once for a new RE app-data store.
2. Protect it with Windows `CryptProtectData` using current-user scope.
3. Do not set `CRYPTPROTECT_LOCAL_MACHINE`.
4. Use non-interactive `CRYPTPROTECT_UI_FORBIDDEN`.
5. Persist only a versioned wrapped-key blob (`cenvalue-re.masterkey`).
6. Unwrap only while opening the encrypted database.
7. Never store the plaintext master key in source, `.env`, the database, normal logs, or repository metadata.

Non-Windows CI uses an in-memory test double only to exercise the key lifecycle. It is not a production key protector.

## Migration contract

- Ordered migrations are explicit Python data, each with immutable version/name/statements.
- Applied versions are recorded in `re_schema_migration`.
- Each unapplied migration executes inside `BEGIN IMMEDIATE` and commits only after every statement succeeds.
- Failure rolls the migration back.
- Unknown/future migration versions fail closed.
- No runtime `ALTER TABLE` loop is used as the primary model.

Schema v1 creates the foundation tables needed by the frozen Epic 0 repository contracts:

- `appraisal_case`;
- `property` + `subject_property`;
- `property` + `comparable_property`;
- `construction_asset`;
- `adjustment_decision`;
- `approval_submission`.

Decimal/money/percentage persistence fields are stored as text where scale must be preserved; this avoids binary-float conversion.

## Repository contract

Framework-independent ports exist for:

- Case;
- Subject Property;
- Comparable Property;
- Construction Asset;
- Adjustment Decision;
- Approval Submission.

The SQLCipher adapter implements those ports. Operational case deletion baseline is archive/soft-delete metadata, not destructive purge.

## Explicitly deferred

This PR does not implement:

- full Gate A.3 table coverage for every later aggregate;
- legacy case import/migration;
- document-vault encryption;
- backup/recovery/export;
- portable cross-machine key recovery;
- appraisal/business APIs;
- valuation formulas;
- Excel runtime;
- UI features.

Those remain governed by the Design Book/Gate A packets and later scoped work.
