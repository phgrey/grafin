import pytest
from mac_graph.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition
from mac_graph.manifest.loader import load_manifest_from_yaml
from mac_graph.adapters import (
    get_adapter_by_name,
    LangGraphAdapter,
    CrewAIAdapter,
    SemanticKernelAdapter,
    YamlGraphAdapter,
)


def test_adapter_factory():
    lg = get_adapter_by_name("langgraph")
    assert isinstance(lg, LangGraphAdapter)

    cr = get_adapter_by_name("crewai")
    assert isinstance(cr, CrewAIAdapter)

    sk = get_adapter_by_name("semantic_kernel")
    assert isinstance(sk, SemanticKernelAdapter)

    yg = get_adapter_by_name("yamlgraph")
    assert isinstance(yg, YamlGraphAdapter)


def test_langgraph_adapter_build_and_export():
    manifest = load_manifest_from_yaml("manifest.yaml")
    adapter = LangGraphAdapter()

    # Build executable StateGraph
    compiled_graph = adapter.build_executable(manifest)
    assert compiled_graph is not None

    # Export compiled StateGraph back to GraphManifest
    exported_manifest = adapter.export_manifest(compiled_graph)
    assert isinstance(exported_manifest, GraphManifest)
    assert len(exported_manifest.nodes) > 0


def test_crewai_adapter_tool_and_acl_hooks():
    adapter = CrewAIAdapter(acl_policy="admin_only_node_deletion")
    manifest = GraphManifest(
        nodes=[NodeDefinition(id="node_1", code_ref="m:f1")],
        edges=[],
    )

    tool = adapter.get_tool_wrapper(manifest)

    # Non-admin attempt to remove node should be DENIED by ACL hook
    res_denied = tool._run(action="remove_node", node_id="node_1", agent_role="user_agent")
    assert "ACL DENIED" in res_denied
    assert len(manifest.nodes) == 1

    # Admin attempt to remove node should succeed
    res_allowed = tool._run(action="remove_node", node_id="node_1", agent_role="admin")
    assert "SUCCESS" in res_allowed
    assert len(manifest.nodes) == 0


def test_semantic_kernel_adapter_plugin_and_filter():
    adapter = SemanticKernelAdapter(filter_allowed_actions=["add_node", "inspect_graph"])
    manifest = GraphManifest(
        nodes=[NodeDefinition(id="node_1", code_ref="m:f1")],
        edges=[],
    )

    plugin = adapter.get_tool_wrapper(manifest)

    # Allowed action 'add_node'
    res_add = plugin.manipulate_graph(action="add_node", node_id="node_2", code_ref="m:f2")
    assert "SUCCESS" in res_add
    assert len(manifest.nodes) == 2

    # Blocked action 'remove_node' not in allowed_actions filter
    res_blocked = plugin.manipulate_graph(action="remove_node", node_id="node_1")
    assert "ACL_DENIED" in res_blocked
    assert len(manifest.nodes) == 2
