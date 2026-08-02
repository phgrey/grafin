import pytest
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition
from graphin.manifest.loader import load_manifest_from_yaml, save_manifest_to_yaml


def test_manifest_schema_and_serialization(tmp_path):
    manifest = GraphManifest(
        version="0.1.0",
        metadata={"name": "test_graph", "description": "GraphInYAML test"},
        nodes=[
            NodeDefinition(id="node_1", type="function", code_ref="module:func1"),
            NodeDefinition(id="node_2", type="function", code_ref="module:func2"),
        ],
        edges=[
            EdgeDefinition(source="node_1", target="node_2"),
        ],
        framework_configs={"langgraph": {"checkpointer": "MemorySaver"}},
    )

    yaml_file = tmp_path / "graphin.yaml"
    save_manifest_to_yaml(manifest, yaml_file)
    assert yaml_file.exists()

    loaded = load_manifest_from_yaml(yaml_file)
    assert loaded.metadata["name"] == "test_graph"
    assert len(loaded.nodes) == 2
    assert loaded.nodes[0].id == "node_1"
    assert loaded.edges[0].source == "node_1"
    assert loaded.edges[0].target == "node_2"


def test_manifest_node_mutation():
    manifest = GraphManifest(
        nodes=[NodeDefinition(id="n1", code_ref="m:f1")],
        edges=[EdgeDefinition(source="n1", target="n2")],
    )

    manifest.add_node(NodeDefinition(id="n2", code_ref="m:f2"))
    assert len(manifest.nodes) == 2

    success = manifest.remove_node("n1")
    assert success is True
    assert len(manifest.nodes) == 1
    assert manifest.nodes[0].id == "n2"
    assert len(manifest.edges) == 0
