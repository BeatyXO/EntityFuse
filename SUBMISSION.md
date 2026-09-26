# Submission brief

**Title:** EntityFuse — Consensus-Backed Entity Reconciliation Primitive

**Category:** Standalone GenLayer Intelligent Contract

EntityFuse reconciles independently registered real-world records into safe canonical identity clusters. Validators independently evaluate whether two records describe the `SAME_ENTITY`, `DIFFERENT_ENTITY`, or have `INSUFFICIENT_EVIDENCE`, using source-grounded semantic reasoning. Consensus does not directly control cluster state: deterministic logic performs safe union, blocks merges across known difference edges, selects canonical roots, and quarantines any cluster that contains an explicit identity contradiction. A typed `EntityGate` consumer demonstrates that another IC can depend on `same_entity(...)` and reject replayed actions. The primitive is intended for registries, reputation systems, marketplaces, compliance, datasets and cross-system identity reconciliation. It is intentionally not a frontend application and not a generic "AI decides if names look similar" demo.

## Reviewer focus

A strong final submission should make these properties easy to verify:

- real semantic necessity for consensus;
- validator independence;
- immutable input records;
- unique namespace/external-ID source keys;
- safe deterministic clustering;
- contradiction handling;
- `INSUFFICIENT_EVIDENCE` as a first-class result;
- typed IC-to-IC reuse;
- adversarial Direct Mode tests;
- real stable-Studionet lifecycle evidence.
