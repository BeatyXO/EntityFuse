# Architecture

## 1. Immutable records

Each registration receives a monotonically increasing `record_id`. A `(namespace, external_id)` source key is unique, so the same source-system record cannot be re-registered under a different local ID. The record contains a namespace, external identifier, display name, jurisdiction, source URL and a bounded JSON attribute object. A record is not editable after registration. This prevents a pair decision from silently changing meaning later.

## 2. Pair adjudication

A canonical unordered pair key is `min_id:max_id`. A pair can be adjudicated once. Consensus must return exactly one of:

- `SAME_ENTITY`
- `DIFFERENT_ENTITY`
- `INSUFFICIENT_EVIDENCE`

The leader and validators independently execute the semantic evaluation. When source URLs are supplied, each validator independently fetches them. User-provided attributes are claims, not decisive proof.

`SAME_ENTITY` must require affirmative identity linkage. `DIFFERENT_ENTITY` must require affirmative identity conflict. Weak evidence must collapse to `INSUFFICIENT_EVIDENCE`.

## 3. Deterministic clustering

Every record begins as its own cluster. Clusters use a deterministic union-find style parent relation.

A `SAME_ENTITY` decision may union two clusters only if there is no already-known `DIFFERENT_ENTITY` edge crossing those clusters. The smaller root ID becomes the canonical root so union order cannot choose a different canonical representative.

## 4. Contradiction quarantine

Entity identity is transitive, so a cluster containing an explicit `DIFFERENT_ENTITY` relationship is unsafe.

If a `DIFFERENT_ENTITY` pair is finalized for two records already in one cluster, the root becomes `INCONSISTENT`. Likewise, if a new `SAME_ENTITY` edge attempts to bridge clusters with a known cross-cluster difference, the union is blocked and the implicated clusters are marked inconsistent.

`same_cluster(a,b)` reports structural membership. `same_entity(a,b)` is stricter: it returns true only when both records share a root **and** that root is `CONSISTENT`.

This distinction is intentional. Downstream contracts should consume `same_entity`, not raw cluster membership.

## 5. No silent repair

The handoff does not include an automatic split/rebuild mechanism. An incorrect finalized SAME edge is not silently rewritten. Contradictions are surfaced as quarantine rather than hidden. If a future version adds recovery, it should be explicit, deterministic and separately reviewed.

## 6. Consumer contract

`EntityGate` uses a typed contract interface and performs a synchronous view call to `same_entity(left,right)`. A successful action hash is consumed exactly once. This proves the primitive can enforce identity-dependent behavior in another IC without copying EntityFuse logic.

## 7. Bounded state

The implementation caps records at 256 because conflict scans are deliberately simple and reviewer-auditable. A production optimization may introduce indexed cluster member sets, but must preserve the same invariants and deterministic roots.
