# 02 — System Architecture
**Status: REVIEWED — Gate A.1 incorporated; Gate A.2 in closure**

## Existing codebase reality
CenValue Manager source of record for reuse is `Reguluspt/New-project`.

Current implementation:
`React/Vite SPA → Flask REST API → Python src services → SQLite/files`

React/Vite infrastructure and selected Python services are reusable. Ant Design is not the target design system; CenValue RE UI contracts remain Astryx.

## Target migration boundary
Target platform remains Windows Desktop/local-first with Tauri 2 preferred.

Gate A.2 recommended runtime boundary:
`Tauri Desktop Shell → React/Astryx UI → loopback-only local application service → framework-independent RE domain → local persistence/adapters`

The existing Flask API may be retained as a transitional local application-service boundary. It is not the target public deployment topology and must not own valuation/domain rules.

## Domain isolation rule
`External/UI/API → Application Service → Canonical Domain → Ports/Adapters`

Valuation/calculation rules, domain validation, canonical models and provenance must not live in Flask blueprints, React components or provider adapters.

## Provider boundary
`External Provider → Adapter/Gateway → Staging/Normalization → Canonical Domain`

Interfaces include `OcrProvider`, `MapProvider`, and `LandRegistryLookupProvider`.

## Offline rule
Manual TSTĐ/TSSS, local historical learning, adjustment, calculation, case management and Excel export remain usable without online providers.

## Persistence direction
Existing SQLite is evidence of viable local persistence, but the existing flat `cases` table is legacy and is not the new canonical schema. New RE bounded persistence is designed separately and can coexist during migration.

## OPEN for Gate A.2/A.3
- Exact Tauri ↔ local-service process lifecycle and IPC/loopback contract.
- Packaging strategy for the Python local service.
- Authentication model for a single-user local desktop runtime.
- Encryption/vault/key management.
