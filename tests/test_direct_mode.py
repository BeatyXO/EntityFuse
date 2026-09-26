import json
import os

import pytest

from gltest.direct import VMContext, deploy_contract


def _deploy(vm, path, *args):
    # gltest's Windows loader closes a temporary stdin file and then unlinks it;
    # keep the file handle usable for this native Direct Mode process.
    original_unlink = os.unlink
    os.unlink = lambda _path: None
    try:
        return deploy_contract(path, vm, *args)
    finally:
        os.unlink = original_unlink


def _records(contract):
    attrs = {"registration_id": "GB-ACME-001", "legal_name": "Acme Holdings Ltd"}
    a = contract.register_record("registry", "a", "Acme Holdings Ltd", "GB", "", attrs)
    b = contract.register_record("registry", "b", "Acme Holdings Limited", "GB", "", attrs)
    c = contract.register_record("registry", "c", "Other Company", "US", "", {"registration_id": "US-OTHER-7"})
    d = contract.register_record("directory", "d", "Acme", "GB", "", {"listing": "Acme"})
    return a, b, c, d


def test_entity_fuse_direct_mode_lifecycle_and_contradiction():
    vm = VMContext()
    with vm.activate():
        fuse = _deploy(vm, "contracts/entity_fuse.py")
        a, b, c, d = _records(fuse)
        assert fuse.get_record_count() == 4

        vm.mock_llm(".*", json.dumps({"decision": "SAME_ENTITY", "reason": "same registration"}))
        assert fuse.resolve_pair(a, b) == "SAME_ENTITY"
        assert fuse.same_cluster(a, b) is True
        assert fuse.same_entity(a, b) is True
        with pytest.raises(Exception):
            fuse.resolve_pair(b, a)

        vm.clear_mocks()
        vm.mock_llm(".*", json.dumps({"decision": "INSUFFICIENT_EVIDENCE", "reason": "ambiguous directory"}))
        assert fuse.resolve_pair(a, d) == "INSUFFICIENT_EVIDENCE"
        assert fuse.same_cluster(a, d) is False
        assert fuse.get_relation(a, d) == "INSUFFICIENT_EVIDENCE"

        # Build a transitive cluster, then add an internal contradiction.
        vm.clear_mocks()
        vm.mock_llm(".*", json.dumps({"decision": "SAME_ENTITY", "reason": "same registration"}))
        assert fuse.resolve_pair(b, c) == "SAME_ENTITY"
        vm.clear_mocks()
        vm.mock_llm(".*", json.dumps({"decision": "DIFFERENT_ENTITY", "reason": "conflict"}))
        assert fuse.resolve_pair(a, c) == "DIFFERENT_ENTITY"
        assert fuse.same_cluster(a, c) is True
        assert fuse.same_entity(a, c) is False
        assert fuse.get_cluster_state(a) == "INCONSISTENT"


def test_entity_gate_direct_mode_typed_read_and_replay():
    vm = VMContext()
    with vm.activate():
        fuse = _deploy(vm, "contracts/entity_fuse.py")
        a, b, c, _ = _records(fuse)
        vm.clear_mocks()
        vm.mock_llm(".*", json.dumps({"decision": "SAME_ENTITY", "reason": "same registration"}))
        fuse.resolve_pair(a, b)
        import genlayer.gl.genvm_contracts as contracts_runtime
        contracts_runtime.__known_contract__ = None
        gate = _deploy(vm, "contracts/entity_gate.py", fuse.address)
        # Direct Mode keeps deployed contracts in separate VM instances. Bridge
        # the generated typed interface to this in-memory fuse instance; the
        # live Studionet lifecycle separately proves the real IC-to-IC call.
        import sys
        gate_module = sys.modules["_contract_entity_gate"]
        fuse_instance = fuse
        class _FuseIface:
            def __init__(self, _address):
                pass
            def view(self):
                return fuse_instance
        gate_module.EntityFuseIface = _FuseIface
        assert gate.execute_if_same_entity(a, b, "action-1") is True
        assert gate.is_consumed("action-1") is True
        with pytest.raises(Exception):
            gate.execute_if_same_entity(a, b, "action-1")
        with pytest.raises(Exception):
            gate.execute_if_same_entity(a, c, "action-2")
