# CenValue Manager RE — Gate A.2 Runtime Boundary Decision

**Date:** 2026-08-15
**Status:** LOGICAL BOUNDARY FROZEN
**Source repository:** `Reguluspt/New-project`

## Decision

CenValue RE will use a desktop-hosted architecture that reuses the current React/Python investment without preserving the public-web deployment topology.

```text
Tauri 2 Desktop Shell
        |
        v
React + Astryx UI
        |
        v
Local Application Service
(Flask retained initially, loopback-only)
        |
        v
Framework-independent RE Domain/Application Modules
        |
        +-- Local Persistence Adapter
        +-- Excel Adapter
        +-- OCR Provider Adapter
        +-- Map Provider Adapter
        +-- VBDLIS/Registry Adapter
```

## Responsibilities

### Tauri desktop shell
Owns:
- Windows desktop application lifecycle.
- Window and packaged-application boundary.
- Starting/stopping/supervising the local Python application-service process.
- Desktop-specific filesystem/dialog integration through controlled commands.
- Packaging/update/security hooks that belong to the desktop host.

Does not own:
- valuation rules;
- adjustment calculations;
- property schema;
- historical-learning rules.

### React + Astryx
Owns:
- Case Portfolio and Workbench UI.
- input/edit/review interactions;
- keyboard workflow;
- readiness/context presentation.

Rules:
- UI never talks directly to SQLite, Excel files, OCR, Maps or VBDLIS.
- Existing React/Vite infrastructure is reusable.
- Existing Ant Design components are migration inputs, not the target design system.

### Local application service
Initial implementation: reuse Flask API because the current repository already has production route/application patterns and integration tests.

Target behavior:
- local/loopback-only;
- not a public web service;
- acts as application-service/API boundary;
- delegates business rules to domain/application modules;
- contains no new valuation formulas in blueprints.

The desktop target no longer requires Flask to serve the React SPA; Tauri hosts the UI. Flask is retained for local API compatibility during migration.

### Framework-independent RE domain/application modules
Own:
- canonical schemas/entities/value objects;
- case lifecycle invariants;
- construction valuation;
- adjustment rules/calculation graph;
- comparable-quality metrics;
- valuation result;
- historical-learning contracts;
- provenance/audit rules;
- approval/revision semantics.

These modules must not import Flask, React, Tauri or concrete provider SDKs.

### Ports/adapters
Concrete infrastructure is behind ports:
- persistence;
- Excel;
- OCR;
- Maps/geocoding;
- Registry/VBDLIS;
- document vault.

## FastAPI decision

Do **not** migrate Flask to FastAPI solely because FastAPI already exists in `requirements.txt` or because it is newer/preferred in another project.

A Flask→FastAPI migration is deferred unless a measurable requirement appears that cannot be met cleanly by the local Flask application-service boundary.

This prevents a framework rewrite from delaying the appraisal domain.

## Migration strategy

1. Keep legacy CenValue Manager modules operational.
2. Create a new `re` bounded domain/application area.
3. New RE routes call application services, not legacy SQL helpers directly.
4. Reuse selected utilities through adapters.
5. Migrate React pages progressively to the new RE API/contracts and Astryx.
6. Desktop-pack the local service after the Walking Skeleton contracts stabilize.

## Security boundary carried to later Gate

The runtime is local-only, but local-only does not mean trusted by default.
Gate Security must still decide:
- backend bootstrap/auth token;
- port binding/lifecycle;
- local secret storage;
- DB/vault encryption;
- backup/restore.

## Acceptance

Gate A.2 logical runtime boundary is frozen when:
- no public web dependency is required for core workflows;
- UI cannot bypass application services to reach storage/providers;
- Flask is explicitly transitional infrastructure, not the domain;
- Python domain is framework-independent;
- no FastAPI rewrite is required for Epic 0/1.
