# CenValue RE — Astryx Reference Correction

**Date:** 2026-08-15
**Status:** CORRECTION APPLIED

## Correction
The existing CenValue Manager repository `Reguluspt/New-project` does **not** currently use Astryx. It uses Ant Design.

Astryx is the **target design system for CenValue RE**, to be introduced deliberately based on the official Astryx documentation.

## Official Astryx baseline
- Astryx is an open-source, customizable design system.
- Current official documentation states React 19+ is required.
- Official packages include `@astryxdesign/core`, themes such as `@astryxdesign/theme-neutral`, and `@astryxdesign/cli`.
- Astryx supports StyleX integration and also supports plain CSS/className/Tailwind-style integration patterns.
- Official component library includes App Shell, Side Nav, Tab List, Field, Number Input, Text Input, File Input, Tooltip, Hover Card, Popover, Dialog, Table, Tree List, Progress Bar and other primitives relevant to CenValue RE.
- Astryx provides a Vite example app, so the existing React/Vite base can be migrated without changing frontend framework.

## CenValue RE consequence
Do not describe Astryx as something reusable from the current CenValue Manager UI.

Correct migration statement:
`Existing React/Vite infrastructure + existing business UX knowledge → migrate visual/component layer from Ant Design/custom CSS to Astryx for CenValue RE`.

## Migration safety
Astryx documentation warns that existing global CSS/resets can override Astryx layers. Before building CenValue RE screens:
1. inventory existing global CSS and Ant Design dependencies;
2. establish CSS cascade-layer order;
3. create a small Astryx integration spike;
4. migrate screen-by-screen, not through a blind global replacement.

## Initial component mapping for CenValue RE
- Workbench shell → App Shell + Side Nav + Layout/Section.
- TSTĐ/TSSS forms → Field + Form Layout + Text/Number/Date inputs.
- Case status/readiness → Badge + Status Dot + Progress Bar.
- Context Drawer → Overlay/Popover/Hover Card patterns, with a dedicated resizable panel where required.
- Adjustment Grid → Astryx Table may provide visual primitives, but spreadsheet-grade keyboard/editing behavior remains a custom Workbench component/domain UI requirement and must not be constrained by the generic Table API.
- Historical suggestion hover → Tooltip/Hover Card/Popover.
- File/GCN intake → File Input.
- Revision/approval navigation → Tab List / Metadata List / List as appropriate.

## Rule
Astryx is a design-system dependency, not a domain dependency. CenValue RE business contracts must remain independent of Astryx component APIs.
