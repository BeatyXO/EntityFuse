# Threat model

## Malicious registrant

A user can submit misleading names or attributes. Therefore user-supplied fields are never treated as sufficient proof of identity. Validators must ground decisive outcomes in the supplied evidence sources when they are used.

## Prompt injection in fetched pages

Fetched source content is untrusted evidence. The evaluation prompt explicitly instructs validators to ignore instructions embedded in source text.

## Malicious leader

A leader may propose a well-formed but false decision. Validators must independently re-fetch/re-evaluate and compare the decision-bearing enum. Schema validation alone is insufficient.

## Source outage or ambiguity

Unavailable or weak evidence must produce `INSUFFICIENT_EVIDENCE`, not optimistic SAME/DIFFERENT inference.

## Transitive contradiction

`A=SAME B`, `B=SAME C`, and `A=DIFFERENT C` must never remain consumable as a healthy identity cluster. The cluster is quarantined.

## Merge-order manipulation

Canonical root selection must not depend on caller-preferred ordering. Lower root ID wins every safe union.

## Denial through unbounded scans

The contract caps record count. If a future version replaces scans with indexed membership, tests must prove equivalent behavior.

## Replay against consumer

A caller must not reuse a previously accepted action hash in EntityGate.
