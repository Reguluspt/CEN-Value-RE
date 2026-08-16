# E0-PR-001 — Corrective Report v1

**Date:** 2026-08-16  
**Scope:** architecture import guard only  
**Acceptance status:** evidence prepared; not self-declared ACCEPTED

## Finding
The original AST guard compared imports against `re.adapters` but repository imports may be spelled `src.re.adapters`. It also did not resolve relative import levels or alias-only `ImportFrom` forms. This created a real false negative against the E0-PR-001 acceptance requirement that tests enforce the import boundary.

## Corrective
`tests/re/test_architecture_boundaries.py` now:
- canonicalizes absolute `src.*` module paths before matching;
- resolves relative imports against the package containing the scanned file;
- records imported aliases as possible dependency targets;
- self-tests the forbidden spellings:
  - `import re.adapters`;
  - `import src.re.adapters.persistence`;
  - `from src.re.adapters import persistence`;
  - `from src.re import adapters`;
  - `from ...adapters import persistence`;
  - `from ... import adapters`;
- verifies a normal `from src.re import domain` import is not rejected.

## Evidence
Baseline artifact suite before corrective: **4 passed**.

Corrected focused suite:

```text
......                                                                   [100%]
6 passed in 0.03s
```

Mutation 1 inserted `from src.re.adapters import persistence` in `src/re/domain/cases/__init__.py` and the domain architecture test failed with `re.adapters` / `re.adapters.persistence` violations.

Mutation 2 inserted `from ...adapters import persistence` in the same domain package and the architecture test failed with the same normalized violations.

The mutation file was restored after each run and the final focused suite returned 6/6 green.

## Scope control
No business entity, valuation formula, persistence implementation, Excel adapter implementation, Flask/API wiring, Astryx code, or production dependency was added by this corrective.
