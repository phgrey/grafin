import pytest
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition
from graphin.manifest.loader import load_manifest_from_yaml
from graphin.adapters import (
    get_adapter_by_name,
    LangGraphAdapter,
    CrewAIAdapter,
    SemanticKernelAdapter,
    GraphInYAMLAdapter,
)


def test_adapter_factory():
    lg = get_adapter_by_name("langgraph")
    assert isinstance(lg, LangGraphAdapter)

    cr = get_adapter_by_name("crewai")
    assert isinstance(cr, CrewAIAdapter)

    sk = get_adapter_by_name("semantic_kernel")
    assert isinstance(sk, SemanticKernelAdapter)

    gy = get_adapter_by_name("graphin_yaml")
    assert isinstance(gy, GraphInYAMLAdapter)


def test_langgraph_adapter_build_and_export():
    manifest = load_manifest_from_yaml("examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml")
    adapter = LangGraphAdapter()

    compiled_graph = adapter.build_executable(manifest)
    assert compiled_graph is not None

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

    res_denied = tool._run(action="remove_node", node_id="node_1", agent_role="user_agent")
    assert "ACL DENIED" in res_denied
    assert len(manifest.nodes) == 1

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

    res_add = plugin.manipulate_graph(action="add_node", node_id="node_2", code_ref="m:f2")
    assert "SUCCESS" in res_add
    assert len(manifest.nodes) == 2

    res_blocked = plugin.manipulate_graph(action="remove_node", node_id="node_1")
    assert "ACL_DENIED" in res_blocked
    assert len(manifest.nodes) == 2
