# CenValue Manager RE — Gate A.1 Repository & Reuse Audit

**Date:** 2026-08-15
**Repository audited:** `Reguluspt/New-project`
**Branch:** `main`
**Status:** COMPLETED — design input for Gate A.2

## 1. Existing architecture observed

The current CenValue Manager repository is a web-oriented application:
- Frontend: React SPA under `web/`, Vite-based.
- UI library: Ant Design, not Astryx.
- API: Flask REST API under `api/`.
- Core/business/data services: Python modules under `src/`.
- Persistence: SQLite through `src/sqlite_store.py`.
- Excel: openpyxl is already used.
- Existing source also contains administrative-address conversion, document/export, AI/OCR-related and case-management modules.

The existing README explicitly describes `React SPA → Flask API → src/Data Layer`.

## 2. Reuse classification

### REUSE / ADAPT
- `web/` React application structure, routing patterns, React Query/API-client patterns where compatible.
- `api/` Flask application factory/blueprint patterns as a transitional local application-service layer.
- Case-management behavior: list/search/filter/create/update case workflows.
- `src/administrative_address.py` as a candidate reusable domain/service component after contract review.
- Existing local file/document organization concepts.
- openpyxl-based Excel handling utilities as technical building blocks only.
- Existing tests and fixtures that prove current behavior where relevant.

### REFACTOR BEFORE DOMAIN USE
- `src/sqlite_store.py`: current `cases` table is a wide legacy record with mixed concerns. Do not extend it into the new canonical real-estate appraisal schema.
- `api/blueprints/cases.py`: route layer currently queries legacy tables directly. New RE domain must be accessed through application/domain services rather than adding more SQL/valuation rules to blueprints.
- Existing address conversion: retain algorithms/data assets where useful, but wrap them behind the new Address Resolver contract with provenance/versioning.
- Existing OCR/AI utilities: wrap behind provider abstractions and staging/human-review contracts.
- Existing frontend screens/components: reuse interaction and infrastructure selectively, but migrate visual primitives to Astryx contracts rather than perpetuating Ant Design as the product design system.

### DO NOT REUSE AS THE NEW CONTRACT
- Current flat `CASE_FIELDS` / single `cases` table as canonical appraisal data model.
- Current generic `case_excel_export.py` as the legacy appraisal-workbook adapter. It creates a fresh tabular workbook and does not preserve/fill the complex legacy appraisal workbook.
- Current Flask HTTP deployment/VPS topology as the target production architecture for CenValue RE.
- Dashboard/CRM-like modules as GĐ1 core scope unless directly needed by the closed appraisal loop.

## 3. Key architecture mismatch found

The current frontend package depends on Ant Design, while the CenValue RE Design Book requires Astryx. Therefore:
- React/Vite infrastructure is reusable.
- Ant Design-specific visual components are migration candidates, not the target design contract.

The current README describes a web production deployment where Flask serves the built SPA. This conflicts with the CenValue RE target of Windows desktop/local-first. Therefore the HTTP/API layer can be retained only as a local transitional service boundary, not as a public web dependency.

## 4. Persistence finding

`src/sqlite_store.py` is useful evidence that SQLite/WAL and case CRUD already work locally, but the current schema is not suitable as the new canonical schema. Gate A must create new bounded tables/aggregates for:
- AppraisalCase
- SubjectProperty
- ComparableProperty
- ConstructionAsset
- AdjustmentDecision / AdjustmentObservation
- ValuationResult
- ApprovalSubmission / ApprovalCycle
- Provenance / audit
- CaseWorkspaceState

Migration/adapters may read legacy data, but new RE code must not keep adding appraisal logic to the existing flat table.

## 5. Excel finding

Existing `case_excel_export.py` proves openpyxl is already part of the stack, but it only creates a new simple workbook from rows. It is **not** a reusable implementation of the required `ExcelTemplateProfile` / formula-preserving legacy-workbook adapter.

Reuse: Python/openpyxl capability and small utility patterns.
Replace/design anew: workbook fingerprinting, cell/range mapping, formula protection, recalculation/checkpoint verification, approval-return import.

## 6. Gate A.1 decision

**Decision:** Reuse `Reguluspt/New-project` as the source code base/reference implementation, but do not evolve CenValue RE by simply adding fields/routes to the existing legacy case schema.

Adopt a strangler-style internal architecture:
1. Keep existing application running.
2. Add a new RE bounded domain/application layer.
3. Adapt existing React/API/storage utilities around the new domain.
4. Gradually route RE workflows through the new canonical contracts.
5. Keep legacy modules isolated where they serve old CenValue Manager workflows.

## 7. Input to Gate A.2

Gate A.2 must freeze the desktop runtime boundary. Recommended direction based on repository reality:
- Tauri 2 desktop shell for product packaging/window/security boundary.
- Existing React/Vite frontend is reused and migrated to Astryx.
- Existing Flask API is retained initially as a **loopback-only transitional application service**, packaged/started with the desktop app.
- Core RE domain logic must be framework-independent Python modules so Flask can later be replaced or bypassed without rewriting valuation logic.
- Do not migrate Flask to FastAPI solely for technology preference; a migration requires a concrete benefit and separate decision.

