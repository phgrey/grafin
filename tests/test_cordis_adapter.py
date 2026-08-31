import pytest
from graphin.manifest.schema import GraphManifest, NodeDefinition
from graphin.adapters.cordis_adapter import CordisAdapter
from graphin.adapters import get_adapter_by_name
from graphin.skillset.manager import SkillsetManager, CordisSkillsetService
from graphin.cordis.context import Context


def test_cordis_adapter_lookup():
    adapter = get_adapter_by_name("cordis")
    assert isinstance(adapter, CordisAdapter)
    assert adapter.framework_name == "cordis"


def test_cordis_adapter_build_executable():
    adapter = CordisAdapter()
    manifest = GraphManifest(
        version="0.1.0",
        metadata={"name": "test_cordis_manifest"},
        nodes=[
            NodeDefinition(id="node_a", type="function", code_ref="module.func_a"),
            NodeDefinition(id="node_b", type="function", code_ref="module.func_b"),
        ],
        edges=[],
        connections=[],
    )

    ctx = adapter.build_executable(manifest)
    assert isinstance(ctx, Context)
    assert ctx.has_service("node_node_a")
    assert ctx.has_service("node_node_b")

    # Test running a node via Cordis event bus
    res = ctx.emit("cordis/run_node", "node_a", {"input_key": "val"})
    assert len(res) == 1
    assert res[0]["node_id"] == "node_a"
    assert res[0]["status"] == "executed"


def test_cordis_skillset_service():
    ctx = Context()
    skillset_service = CordisSkillsetService(ctx)

    assert ctx.has_service("skillset")

    manifest = GraphManifest(
        version="0.1.0",
        metadata={"name": "topology_test"},
        nodes=[NodeDefinition(id="n1", type="function", code_ref="ref")],
        edges=[],
        connections=[],
    )

    walk_res = ctx.skillset.walk(manifest)
    assert walk_res["manifest_name"] == "topology_test"
    assert walk_res["node_count"] == 1
