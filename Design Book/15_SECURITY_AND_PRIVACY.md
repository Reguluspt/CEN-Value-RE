# 15 — Security & Privacy
**Status: REVIEWED — BASELINE FROZEN; pilot recovery details open**

CenValue RE is Windows Desktop/local-first because appraisal files contain confidential information.

## At-rest baseline
- SQLite-family canonical DB, encrypted at rest (SQLCipher-class capability).
- New RE DB is separate from legacy `cases.db`.
- Random application master key protected by Windows user-scoped DPAPI.
- No plaintext DB key in source, `.env` or DB.
- Document/evidence vault encrypted with authenticated encryption through a vetted library.
- Temporary plaintext files have minimum lifetime and are cleaned after use.

Microsoft documents that DPAPI `CryptProtectData` normally protects data so the same user credentials/machine context are required to decrypt it; this matches the GĐ1 single-user Windows model.

## Local service
- Loopback-only.
- Tauri supervises local service.
- Per-launch local session/bootstrap secret.
- No normal bind to LAN/public interfaces.
- Provider secrets use protected secret storage.
- Logs redact high-sensitivity fields.

## Backup
Plain ZIP backups from the legacy application are not acceptable for RE.
Automatic backup stores encrypted DB/vault artifacts and integrity/version metadata.
Portable cross-machine restore requires a separate explicit recovery-key design.

## Retention
Operational delete is soft-delete/archive by default. Permanent purge is explicit/policy-controlled. Historical Learning inclusion is independent from retention.

## OPEN before pilot
Exact SQLCipher binding/distribution, document crypto library, portable backup/recovery, installer/update signing, provider retention/deletion policy.
