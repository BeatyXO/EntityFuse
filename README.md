# EntityFuse

EntityFuse is a standalone GenLayer Intelligent Contract primitive for **consensus-backed real-world entity reconciliation**.

It answers a narrow semantic question that deterministic smart contracts cannot reliably answer: **do two independently registered records refer to the same real-world entity?** GenLayer consensus produces one of three pair outcomes:

- `SAME_ENTITY`
- `DIFFERENT_ENTITY`
- `INSUFFICIENT_EVIDENCE`

The AI/validator layer does **not** control cluster state directly. EntityFuse applies deterministic union and contradiction rules after consensus. A known `DIFFERENT_ENTITY` edge blocks a cluster merge. If a later `DIFFERENT_ENTITY` relationship appears inside an already fused cluster, the cluster becomes `INCONSISTENT`, and `same_entity(...)` returns false until a future, explicitly designed recovery mechanism is introduced.

## Product boundary

EntityFuse is a reusable IC primitive, not an application. **There is no frontend.**

A second contract, `EntityGate`, demonstrates real IC-to-IC consumption: an action can execute only when two record IDs currently resolve to one **consistent** EntityFuse cluster, and action hashes cannot be replayed.

## Why GenLayer

Entity identity frequently depends on qualitative evidence: legal names, registration identifiers, jurisdictions, official pages, contact domains, aliases, historical naming and conflicting records. Pure byte equality is too weak; unconstrained LLM judgment is too unsafe.

EntityFuse therefore separates responsibilities:

1. immutable, namespace-keyed record registration;
2. validator-independent source retrieval and semantic pair adjudication;
3. deterministic pair storage;
4. deterministic cluster union;
5. deterministic contradiction/quarantine handling;
6. typed downstream consumption.

## Stable network target

- network: `studionet`
- chain ID: `61999`
- RPC: `https://studio.genlayer.com/api`
- explorer: `https://explorer-studio.genlayer.com`

## Repository map

- `contracts/entity_fuse.py` — primary primitive
- `contracts/entity_gate.py` — typed downstream consumer
- `tests/test_protocol_model.py` — adversarial deterministic protocol tests
- `docs/ARCHITECTURE.md` — protocol design
- `docs/INVARIANTS.md` — invariants reviewers should verify
- `docs/THREAT_MODEL.md` — trust boundaries and abuse cases
- `fixtures/` — immutable public evidence fixtures for live lifecycle proof
- `scripts/preflight.py` — repository/finality checks
- `scripts/pin_fixture_commit.py` — converts fixture URLs to immutable GitHub raw URLs
- `DEPLOYMENT.md` — live evidence only; must never contain invented addresses or tx hashes
- `SUBMISSION.md` — intended category and reviewer summary

## Local deterministic tests

```bash
python -m pytest -q
python scripts/preflight.py
```

The handoff intentionally contains no claimed live deployment. The finishing agent must run the real GenVM lint/validation, Direct Mode and Studionet lifecycle and record only evidence it actually obtains.
