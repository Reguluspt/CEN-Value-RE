# CenValue RE — Epic 0 Engineering Foundation Design Freeze v1

**Status:** READY FOR IMPLEMENTATION PACKETS  
**Source code base/reference:** `Reguluspt/New-project`

## 1. Runtime boundary
```text
Tauri 2 Desktop Shell
  -> React 19 + Astryx UI
  -> loopback-only local Flask application service (transitional)
  -> framework-independent `re` domain/application packages
  -> persistence / Excel / provider adapters
```

No new valuation formulas in React, Flask blueprints, Tauri commands or database helpers.

## 2. Proposed additive repository structure

Do not rewrite legacy folders. Add a bounded RE area:

```text
src/
  re/
    domain/
      cases/
      property/
      construction/
      adjustment/
      valuation/
      approval/
      common/
    application/
      commands/
      queries/
      services/
    ports/
      persistence.py
      excel.py
      providers.py
    adapters/
      persistence/
      excel/
      providers/

api/
  blueprints/
    re_cases.py
    re_health.py

web/src/
  re/
    app/
    pages/
    components/
    features/
    api/
    design-system/

desktop/
  tauri/
```

Exact file names may be adjusted to repository conventions, but the dependency direction is frozen.

## 3. Dependency direction
Allowed:
`UI/API -> Application -> Domain -> Port interfaces`
`Adapters -> Port interfaces + Domain types`

Forbidden:
- Domain importing Flask/Tauri/React/Astryx/openpyxl/provider SDK.
- React directly reading SQLite/Excel/provider.
- Flask blueprint embedding calculation formulas.
- New RE fields added to the legacy wide `cases` table.

## 4. Astryx integration rule
Current repo uses Ant Design. Astryx is introduced only for CenValue RE surfaces.

Epic 0 performs one isolated integration spike:
- React 19/Vite compatibility.
- CSS cascade/global reset collision check.
- App Shell + Side Nav + Form primitives.
- No global rewrite of existing CenValue UI.

## 5. Persistence baseline
- Separate encrypted RE SQLite-family database.
- Explicit migrations.
- Windows-protected key baseline.
- Repository interfaces around persistence.
- Legacy `cases.db` accessed only through explicit adapter/import paths.

## 6. Numeric primitives
Framework-independent:
- Decimal money.
- Decimal percentage.
- canonical units.
- Excel-compatible nearest rounding.
- `RoundingPolicy`.
- raw vs rounded value.

## 7. Excel infrastructure
Epic 0 builds infrastructure only:
- `ExcelTemplateProfile`.
- fingerprint/formula signatures.
- cell-class metadata.
- compatibility transformation registry.
- unsupported-template fail-safe.
- golden-fixture loader.

Full input fill/calculation output adapter belongs to Epic 1.

## 8. Repository governance
> **Governance supersession — 2026-08-16:** latest Project Owner/session-handoff instruction permits server-first implementation/verification and removes `H:\CEN Manage` as a mandatory gate. This supersedes only the local-first verification requirement below; it does **not** authorize GitHub/VPS publication.

Historical `AGENTS.md` baseline recorded when this freeze was written:
- source code change first applied and verified in local Windows beta app `H:\CEN Manage`;
- GitHub/VPS deployment only after explicit user direction;
- surgical changes and focused verification.

Current rule: surgical/focused verification remains required; GitHub/VPS deployment still requires explicit Project Owner direction. These design packets do not authorize direct source writes to GitHub.
