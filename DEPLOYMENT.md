# Live deployment evidence

Network: stable Studionet, chain ID `61999`.
RPC: `https://studio.genlayer.com/api`.
Fixture commit: `8a71fb5116574cd7063ef7e16565eaba83d36c28`.

## EntityFuse

- Address: `0xD84d155D2dF7469711BFc2428832Ec0d18049aDD`
- Deployment transaction: `0x67c460b6c1d36aba95475ae48b3c5f9b046c5f66cce39151236778ac3057c8dc`
- Record 1 registration: `0x8d15c74c2d99bf73d5fe1c13443066f9f25f76eb34ce1024c9745b07485daf45`
- Record 2 registration: `0x39886d78a6f05b6717206cae983b07a19baba021710fdc4e3a67c5b0b7fc5f9c`
- Record 3 registration: `0x89b7d46a883804c75335878b863a91a193c9ffc90f2820beedd80a07e2fe8349`
- Record 4 registration: `0x1e18a16a74ed80daf67656e12234d91b2f5b890ec7a67e8dd30fbfdcf5ddba2b`
- Record 5 (weak ambiguous fixture) registration: `0x48d831bb96f360d2aa83851195553837728cc6ace12a51f9eb3c1eb793f6b936`
- Verified record count: `5`

Pair outcomes:

- Records `1,2`: `SAME_ENTITY`; transaction `0xa600408b3cbae592eab1f47529e1cb5687a79d0aa02b92768a8639b82fa92a10`; `same_entity(1,2)` returned `true`.
- Records `1,3`: `DIFFERENT_ENTITY`; transaction `0x98e80ba306a15380ca7b0cb029e0cdfb91de74461b6edb99b452a86b2535edb1`; `same_cluster(1,3)` returned `false`.
- Records `1,4`: remained `UNRESOLVED` after transactions `0x4505f2934d82004739f8244b6470e29257e7be50c7457e2d7f22a9bc94fbcd39` and `0x6bcaa67df69d9c5d21e8f55d31d8ac37d6cc7b601e9fae84703c0e271eedde4e`; validator disagreement prevented a decisive result.
- Records `4,5`: `INSUFFICIENT_EVIDENCE`; transaction `0x3018122235bb46b3b40c5558c5c7cf54f27fb0f917b061216e98f2ef7d3b8283`; `get_relation(4,5)` returned `INSUFFICIENT_EVIDENCE`, `same_cluster(4,5)` returned `false`, and `same_entity(4,5)` returned `false`.

## EntityGate

- Address: `0x6D38c1Ee4F9575d6047c539D3105aEaC9faCe7F2`
- Deployment transaction: `0xb06112c7f2ca18a1d4fd1bfe7314e62c5d48e4a3909a977157bec040d798248d`
- Healthy action transaction: `0xfa3d6a69b661c93c947db958b80189c890fbc9eeb4d2c471aadf2b994d80e6b1`
- `is_consumed("action-healthy-001")` returned `true`.
- Replay transaction `0x20b9ff7fec8a3492c349b216f26f53d99165f8f007ddacd0f14ae661d527793b` was rejected and rolled back.

## Verification

- `python scripts/preflight.py`: passed.
- `python -m pytest -q tests/test_direct_mode.py`: 2 passed (actual GenLayer Direct Mode contract execution, including typed gate logic and replay protection).
- `python -m pytest -q`: 18 passed.
- `genvm-lint check --json contracts/entity_fuse.py`: passed lint and SDK validation.
- `genvm-lint check --json contracts/entity_gate.py`: passed lint and SDK validation.

The Direct Mode suite proves the transitive contradiction state (`same_cluster == true`, `same_entity == false`, `INCONSISTENT`) and EntityGate rejection/replay behavior against the contract implementation. A separate live transitive contradiction transaction has not been claimed because the already-finalized production records do not provide a semantically valid SAME sequence across the known DIFFERENT edge; no fabricated live result is recorded.

Final repository commit containing this evidence: recorded by Git after this documentation update.
