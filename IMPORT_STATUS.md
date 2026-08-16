# Initial Project Import Status

**Source workspace:** ChatGPT Library `/CEN Value RE`  
**Target repository:** `Reguluspt/CEN-Value-RE`  
**Import branch:** `agent/initial-project-import`  
**Mode:** Draft PR / review-first import

## Repository scope

The normalized Library snapshot contains 100 project files after duplicate removal. Project Owner has approved a GitHub scope that intentionally excludes reference/sample and packaged binary artifacts:

- `*.pdf` — sample GCN/reference documents;
- `*.xlsx` — sample Excel workbook used for reverse-engineering and qualification;
- `*.zip` — generated/packaged implementation archives whose reviewable patch/report/evidence remains version-controlled.

Those assets remain in the canonical project Library and are not required for the GitHub baseline.

## Version-controlled content

GitHub is intended to contain the reviewable/source-of-truth artifacts needed to continue engineering work, including:

- Design Book;
- Gate A / Gate B contracts and evidence;
- Epic 0 packets;
- corrective register and acceptance evidence;
- canonical fixtures and mapping data;
- implementation patches and reports;
- text logs, hash manifests, and engineering reports.

`BRAINSTORM Full.md` is treated as a Library-only provenance archive rather than an implementation source of truth; current decisions must come from the latest handoff, Gate closure, Design Book, and specialized contracts.

## Current project stage

- Gate B: **FROZEN / CLOSED**.
- E0-PR-001: **ACCEPTED** after independent review.
- E0-PR-002: implementation/static verification prepared; runtime build/browser acceptance evidence remains pending.

## Integrity rule

No excluded binary is replaced by a placeholder or transformed copy. If a binary artifact later becomes necessary for a release, reproducible test, or source-of-truth requirement, it must be introduced deliberately with an explicit repository policy change.

## Merge rule

The first import may be merged when the intended version-controlled file set is present, the PR diff is reviewed, and no unintended binary artifacts are included.
