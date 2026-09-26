# Invariants

A review-ready EntityFuse must preserve all of these:

1. **Unique source key** — a `(namespace, external_id)` pair may be registered only once.
2. **Record immutability** — a registered record's identity-bearing fields never mutate.
3. **Canonical pair key** — `(a,b)` and `(b,a)` address one relationship.
4. **Single finalized pair outcome** — a pair cannot be silently re-adjudicated into a new value.
5. **Three-state semantic result** — only SAME, DIFFERENT or INSUFFICIENT are valid.
6. **Insufficient evidence never merges** — uncertainty is not identity.
7. **Known difference blocks union** — clusters connected by any finalized DIFFERENT edge cannot be safely fused.
8. **Internal difference quarantines** — a DIFFERENT edge inside one cluster makes that cluster inconsistent.
9. **Deterministic root** — safe union selects the lower root ID.
10. **Consumer safety** — `same_entity` is false for inconsistent clusters even when `same_cluster` is true.
11. **Validator independence** — decisive classification cannot be accepted based only on leader formatting or leader prose.
12. **Source grounding** — decisive SAME/DIFFERENT judgments must be supported by independently observed evidence; weak/unavailable evidence becomes INSUFFICIENT.
13. **Nondeterministic purity** — no storage write or cross-contract side effect occurs inside nondeterministic execution.
14. **Replay protection** — EntityGate cannot execute the same `action_hash` twice.
15. **No fabricated proof** — docs never claim deployment/test evidence that was not actually produced.
