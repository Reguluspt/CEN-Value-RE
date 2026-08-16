# CenValue RE — Epic 0 Acceptance Matrix v1

| Area | Required proof |
|---|---|
| Domain isolation | automated import/dependency test |
| Astryx spike | RE shell renders; legacy UI unchanged |
| Decimal | no binary float in appraisal calculation primitives |
| RoundingPolicy | default + override + custom increment tests |
| Template profile | exemplar accepted; mutated signature rejected |
| Golden fixture | versioned fixture loads/checkpoints resolve |
| Local service | loopback-only + session/bootstrap verification |
| Persistence | encrypted RE DB + migrations + repository contract |
| Legacy safety | existing flat `cases` schema not extended for RE |
| Secrets | no plaintext production key/secret |
| Excel qualification | harness cannot claim PASS without real Excel |
| CI | focused Epic 0 suite green |

## Exit gate
Epic 0 is complete only when all rows have explicit evidence.

Passing unit tests alone is insufficient if Astryx integration, encrypted persistence or local-service security evidence is missing.
