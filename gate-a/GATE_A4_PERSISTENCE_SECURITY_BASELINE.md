# CenValue Manager RE — Gate A.4 Persistence & Security Baseline

**Date:** 2026-08-15
**Status:** BASELINE FROZEN; library/package selection remains implementation detail

## 1. Findings from existing CenValue Manager

Current repository stores the primary case database at `data/cases.db` using ordinary SQLite and creates ZIP backups of databases/configuration files. This is acceptable evidence for local-first behavior, but it does not meet the new CenValue RE confidentiality requirement because:
- the database is not encrypted at rest;
- backup ZIPs are not encrypted;
- the existing flat schema mixes legacy case-management concerns.

## 2. Persistence decision

### Database engine
Keep the SQLite family for GĐ1 because:
- the application is single-user/local-first;
- existing code, CRUD patterns and WAL behavior already use SQLite;
- no multi-user server database is required for the closed appraisal loop.

The new RE database is separate from legacy `cases.db`.

Proposed logical files:
```text
app-data/
├── cenvalue-re.db           # encrypted canonical DB
├── vault/                   # encrypted source/output documents
├── cache/                   # disposable, non-authoritative
└── backups/                 # encrypted backup packages
```

### Encryption
Use an encrypted SQLite implementation compatible with the SQLite model (SQLCipher-class capability) for the canonical database.

Database key strategy:
1. Generate a random application master key.
2. Protect/wrap that key using Windows user-scoped DPAPI.
3. Store only the protected key material on disk.
4. Unprotect it only for the running user's session.
5. Never store the plaintext database key in `.env`, source files or the database.

Reason for user-scoped DPAPI: Windows DPAPI normally binds protected data to the same user's logon credentials and machine context, which fits the desktop/local confidentiality model.

### Document vault
Source GCN/images, historical workbooks, generated approval workbooks and other evidence must not be stored as unprotected copies inside the application data directory.

Vault design:
- content-addressable or UUID-based filenames; original filename stored as metadata;
- authenticated encryption using a vetted cryptographic library;
- per-file nonce/metadata;
- master/key material derived from the same protected application secret hierarchy;
- integrity failure must stop document use and surface an error;
- no custom cryptographic primitive implementation.

Temporary plaintext files needed for Excel/preview/provider upload:
- created only in a controlled temp area;
- minimum lifetime;
- deleted/cleaned after operation;
- never treated as authoritative storage.

## 3. Database migration/versioning

New RE schema uses explicit ordered migrations.

Rules:
- no runtime `ALTER TABLE` loops as the primary migration model for new RE domain;
- schema version is recorded;
- migration is transactional when possible;
- migration failure leaves the prior database recoverable;
- legacy `cases.db` is read through an adapter/import path, not automatically reshaped in place.

## 4. Backup baseline

The current plain ZIP backup pattern must not be reused unchanged.

Automatic local backup:
- backup encrypted DB + encrypted vault artifacts/manifest;
- preserve schema/app version and checksums;
- retention policy configurable;
- backup must not contain plaintext secrets.

Portable cross-machine backup is a separate capability because DPAPI user-scoped key wrapping is machine/user bound. Portable export requires an explicit recovery/export key design and is **deferred until before pilot release**, not silently solved with plaintext ZIP.

## 5. Local service security

Loopback-only Flask is transitional but still authenticated.

Baseline:
- bind only to loopback;
- Tauri starts the service and obtains a per-launch bootstrap/session secret;
- browser-style fixed default credentials are not the trust boundary for desktop IPC;
- API requests from the desktop UI carry/derive the current local session credential;
- provider API keys are stored through protected secret storage, never committed to repo or plain `.env` in production;
- external calls are auditable and only send minimum required data.

Exact handshake/port allocation is Epic 0 implementation design, but no endpoint may intentionally bind to all interfaces for normal desktop use.

## 6. Data classes

At-rest sensitivity:
- HIGH: GCN, identity/citizen data, owner names/addresses, appraisal values, approval workbooks, provider tokens.
- MEDIUM: case metadata, adjustment history, internal notes.
- LOW/DISPOSABLE: UI cache, derived thumbnails without personal data (if any).

Logs must redact HIGH data by default.

## 7. Deletion/retention

Deleting a case from UI must not immediately destroy audit/approval history without an explicit retention policy.

GĐ1 baseline:
- operational "delete" is soft-delete/archive at canonical level;
- permanent purge is a separate explicit action/policy;
- temporary provider payloads/cache follow short retention;
- historical-learning inclusion flag is independent from case retention.

## 8. Gate A.4 decision

FROZEN:
- SQLite-family local persistence.
- New separate RE database.
- encrypted-at-rest DB.
- Windows user-scoped DPAPI-protected master key.
- encrypted document vault.
- explicit migrations.
- no plaintext automatic backup.
- loopback-only local service.
- secret/log minimization.

OPEN before pilot:
- exact SQLCipher/Python binding/package distribution;
- exact document-encryption library;
- portable backup/recovery flow;
- installer/update signing and recovery procedures.
