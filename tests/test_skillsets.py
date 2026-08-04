import pytest
from graphin.manifest.schema import GraphManifest, NodeDefinition, ConnectionDefinition
from graphin.skillset import SkillsetManager, StandardGraphSkillset


def test_skillset_protocol_operations():
    manifest = GraphManifest(
        version="0.1.0",
        metadata={"name": "skillset_test"},
        nodes=[
            NodeDefinition(id="n1", type="function", code_ref="m:f1"),
        ],
        connections=[
            ConnectionDefinition(id="db", type="postgres", endpoint="localhost:5432"),
        ],
    )

    manager = SkillsetManager()
    skillset = manager.get_skillset("standard_graph_skillset")
    assert skillset is not None

    topology = skillset.walk_topology(manifest)
    assert topology["node_count"] == 1
    assert topology["connection_count"] == 1

    node_details = skillset.get_node_details(manifest, "n1")
    assert node_details is not None
    assert node_details["id"] == "n1"

    # Mutate node via skillset
    new_node = NodeDefinition(id="n2", type="agent", code_ref="m:f2")
    assert skillset.mutate_node(manifest, new_node) is True
    assert manifest.get_node("n2") is not None

    # Remove node via skillset
    assert skillset.remove_node(manifest, "n1") is True
    assert manifest.get_node("n1") is None
