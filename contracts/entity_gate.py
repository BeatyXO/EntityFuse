# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


@gl.contract_interface
class EntityFuseIface:
    class View:
        def same_entity(self, left: u256, right: u256) -> bool: ...
        def get_cluster_state(self, record_id: u256) -> str: ...

    class Write:
        pass


class EntityGate(gl.Contract):
    """Minimal consumer proving EntityFuse is reusable by another IC."""

    registry: Address
    consumed_actions: TreeMap[str, bool]

    def __init__(self, registry: Address):
        self.registry = registry

    @gl.public.write
    def execute_if_same_entity(self, left: u256, right: u256, action_hash: str) -> bool:
        if action_hash.strip() == "":
            raise gl.vm.UserError("action_hash required")
        if self.consumed_actions.get(action_hash, False):
            raise gl.vm.UserError("action replay")

        registry = EntityFuseIface(self.registry)
        if not registry.view().same_entity(left, right):
            raise gl.vm.UserError("records are not a currently consistent fused entity")

        self.consumed_actions[action_hash] = True
        return True

    @gl.public.view
    def is_consumed(self, action_hash: str) -> bool:
        return self.consumed_actions.get(action_hash, False)
