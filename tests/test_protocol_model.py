import json
import pytest


class Model:
    SAME = "SAME_ENTITY"
    DIFF = "DIFFERENT_ENTITY"
    UNKNOWN = "INSUFFICIENT_EVIDENCE"
    MAX_RECORDS = 256

    def __init__(self):
        self.n = 0
        self.parent = {}
        self.status = {}
        self.rel = {}
        self.records = {}
        self.record_keys = {}
        self.consumed = set()

    def register(self, namespace="registry", external_id=None, display_name="Acme", jurisdiction="", source_url="https://example.com/evidence", attributes_json="{}"):
        if self.n >= self.MAX_RECORDS:
            raise ValueError("record cap reached")
        external_id = external_id or f"id-{self.n + 1}"
        if not namespace.strip() or not external_id.strip() or not display_name.strip():
            raise ValueError("required")
        if len(namespace) > 96 or len(external_id) > 160 or len(display_name) > 240 or len(jurisdiction) > 160:
            raise ValueError("field too long")
        if len(source_url) > 500:
            raise ValueError("source_url too long")
        if source_url and (not source_url.startswith("https://") or any(ch.isspace() for ch in source_url)):
            raise ValueError("bad source")
        if len(attributes_json) > 6000:
            raise ValueError("attributes too large")
        attrs = json.loads(attributes_json or "{}")
        if not isinstance(attrs, dict):
            raise ValueError("attributes object required")
        key = f"{namespace.strip()}::{external_id.strip()}"
        if key in self.record_keys:
            raise ValueError("record key already registered")
        self.n += 1
        self.parent[self.n] = self.n
        self.status[self.n] = "CONSISTENT"
        self.records[self.n] = {"namespace": namespace.strip(), "external_id": external_id.strip(), "attributes": attrs}
        self.record_keys[key] = self.n
        return self.n

    def add(self):
        return self.register()

    def root(self, x):
        seen = set()
        while self.parent[x] != x:
            assert x not in seen
            seen.add(x)
            x = self.parent[x]
        return x

    def key(self, a, b):
        return tuple(sorted((a, b)))

    def relation(self, a, b):
        return self.rel.get(self.key(a, b))

    def members(self, root):
        return [i for i in range(1, self.n + 1) if self.root(i) == root]

    def cross_diff(self, ra, rb):
        return any(self.relation(a, b) == self.DIFF for a in self.members(ra) for b in self.members(rb))

    def resolve(self, a, b, decision):
        if a == b:
            raise ValueError("distinct records")
        if decision not in (self.SAME, self.DIFF, self.UNKNOWN):
            raise ValueError("invalid decision")
        k = self.key(a, b)
        if k in self.rel:
            raise ValueError("pair already resolved")
        self.rel[k] = decision
        if decision == self.UNKNOWN:
            return
        ra, rb = self.root(a), self.root(b)
        if decision == self.DIFF:
            if ra == rb:
                self.status[ra] = "INCONSISTENT"
            return
        if ra == rb:
            return
        if self.cross_diff(ra, rb):
            self.status[ra] = "INCONSISTENT"
            self.status[rb] = "INCONSISTENT"
            return
        winner, loser = sorted((ra, rb))
        if self.status[ra] != "CONSISTENT" or self.status[rb] != "CONSISTENT":
            self.status[winner] = "INCONSISTENT"
        self.parent[loser] = winner

    def same_cluster(self, a, b):
        return self.root(a) == self.root(b)

    def same_entity(self, a, b):
        r = self.root(a)
        return r == self.root(b) and self.status[r] == "CONSISTENT"

    def gate(self, a, b, action):
        if not action.strip():
            raise ValueError("action required")
        if action in self.consumed:
            raise ValueError("replay")
        if not self.same_entity(a, b):
            raise ValueError("not same entity")
        self.consumed.add(action)
        return True


def test_registration_is_immutable_keyed_and_namespace_scoped():
    m = Model()
    a = m.register("sec", "123", "Acme")
    assert m.record_keys["sec::123"] == a
    with pytest.raises(ValueError, match="already registered"):
        m.register("sec", "123", "Acme Alias")
    b = m.register("companies-house", "123", "Acme UK")
    assert b != a


def test_registration_rejects_bad_source_and_non_object_attributes():
    m = Model()
    with pytest.raises(ValueError, match="bad source"):
        m.register(source_url="http://example.com")
    with pytest.raises(ValueError, match="attributes object"):
        m.register(source_url="", attributes_json="[]")


def test_same_unions_with_deterministic_low_root():
    m = Model(); a=m.add(); b=m.add()
    m.resolve(b, a, m.SAME)
    assert m.root(a) == 1 and m.root(b) == 1 and m.same_entity(a, b)


def test_insufficient_never_merges_or_creates_difference():
    m = Model(); a=m.add(); b=m.add()
    m.resolve(a, b, m.UNKNOWN)
    assert not m.same_cluster(a, b)
    assert m.relation(a, b) == m.UNKNOWN


def test_known_difference_blocks_later_union_and_quarantines():
    m = Model(); a=m.add(); b=m.add(); c=m.add()
    m.resolve(a, c, m.DIFF)
    m.resolve(a, b, m.SAME)
    m.resolve(b, c, m.SAME)
    assert not m.same_cluster(a, c)
    assert m.status[m.root(a)] == "INCONSISTENT"
    assert m.status[m.root(c)] == "INCONSISTENT"


def test_internal_difference_quarantines_transitive_cluster():
    m = Model(); a=m.add(); b=m.add(); c=m.add()
    m.resolve(a, b, m.SAME); m.resolve(b, c, m.SAME)
    assert m.same_entity(a, c)
    m.resolve(a, c, m.DIFF)
    assert m.same_cluster(a, c) and not m.same_entity(a, c)


def test_duplicate_pair_rejected_even_if_argument_order_changes():
    m = Model(); a=m.add(); b=m.add(); m.resolve(a, b, m.UNKNOWN)
    with pytest.raises(ValueError, match="already resolved"):
        m.resolve(b, a, m.SAME)


def test_self_pair_and_invalid_decision_are_rejected():
    m = Model(); a=m.add(); b=m.add()
    with pytest.raises(ValueError, match="distinct"):
        m.resolve(a, a, m.SAME)
    with pytest.raises(ValueError, match="invalid decision"):
        m.resolve(a, b, "MAYBE")


def test_transitive_same_relation_is_structural_not_fabricated_pair_result():
    m = Model(); a=m.add(); b=m.add(); c=m.add()
    m.resolve(a, b, m.SAME); m.resolve(b, c, m.SAME)
    assert m.same_entity(a, c)
    assert m.relation(a, c) is None


def test_merge_order_does_not_change_canonical_root():
    m = Model(); a=m.add(); b=m.add(); c=m.add(); d=m.add()
    m.resolve(d, c, m.SAME); m.resolve(b, a, m.SAME); m.resolve(d, a, m.SAME)
    assert all(m.root(x) == 1 for x in (a,b,c,d))


def test_inconsistent_cluster_propagates_if_structurally_merged_before_quarantine():
    m = Model(); a=m.add(); b=m.add(); c=m.add(); d=m.add()
    m.resolve(a,b,m.SAME); m.resolve(c,d,m.SAME); m.resolve(a,c,m.SAME)
    m.resolve(b,d,m.DIFF)
    assert not m.same_entity(a,d)
    assert m.status[m.root(a)] == "INCONSISTENT"


def test_gate_accepts_consistent_cluster_and_blocks_replay():
    m = Model(); a=m.add(); b=m.add(); m.resolve(a, b, m.SAME)
    assert m.gate(a, b, "0xabc") is True
    with pytest.raises(ValueError, match="replay"):
        m.gate(a, b, "0xabc")


def test_gate_rejects_empty_action():
    m = Model(); a=m.add(); b=m.add(); m.resolve(a,b,m.SAME)
    with pytest.raises(ValueError, match="action required"):
        m.gate(a,b,"   ")


def test_gate_rejects_different_entities():
    m = Model(); a=m.add(); b=m.add(); m.resolve(a,b,m.DIFF)
    with pytest.raises(ValueError, match="not same"):
        m.gate(a,b,"act")


def test_gate_rejects_insufficient_and_unresolved_pairs():
    m = Model(); a=m.add(); b=m.add(); c=m.add()
    m.resolve(a,b,m.UNKNOWN)
    with pytest.raises(ValueError, match="not same"):
        m.gate(a,b,"a")
    with pytest.raises(ValueError, match="not same"):
        m.gate(a,c,"b")


def test_gate_rejects_quarantined_cluster():
    m = Model(); a=m.add(); b=m.add(); c=m.add()
    m.resolve(a, b, m.SAME); m.resolve(b, c, m.SAME); m.resolve(a, c, m.DIFF)
    with pytest.raises(ValueError, match="not same"):
        m.gate(a, b, "0xdef")
