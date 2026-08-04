from typing import Dict, Any, List, Optional
from graphin.manifest.schema import GraphManifest, NodeDefinition
from graphin.skillset.base import GraphSkillset


class StandardGraphSkillset(GraphSkillset):
    """Standard GraphIn implementation of the Graph Skillsets Protocol."""

    @property
    def skillset_name(self) -> str:
        return "standard_graph_skillset"

    def walk_topology(self, manifest: GraphManifest) -> Dict[str, Any]:
        return {
            "version": manifest.version,
            "manifest_name": manifest.metadata.get("name", "unnamed_manifest"),
            "node_count": len(manifest.nodes),
            "edge_count": len(manifest.edges),
            "connection_count": len(manifest.connections),
            "nodes": [n.model_dump() for n in manifest.nodes],
            "edges": [e.model_dump() for e in manifest.edges],
            "connections": [c.model_dump() for c in manifest.connections],
        }

    def get_node_details(self, manifest: GraphManifest, node_id: str) -> Optional[Dict[str, Any]]:
        node = manifest.get_node(node_id)
        if node:
            return node.model_dump()
        return None

    def mutate_node(self, manifest: GraphManifest, node: NodeDefinition) -> bool:
        manifest.add_node(node)
        return True

    def remove_node(self, manifest: GraphManifest, node_id: str) -> bool:
        return manifest.remove_node(node_id)

    def get_connections(self, manifest: GraphManifest) -> List[Dict[str, Any]]:
        return [c.model_dump() for c in manifest.connections]


class SkillsetManager:
    """Manager for registering and querying Graph Skillsets across orchestrators."""

    def __init__(self):
        self._skillsets: Dict[str, GraphSkillset] = {}
        self.register_skillset(StandardGraphSkillset())

    def register_skillset(self, skillset: GraphSkillset) -> None:
        """Register a graph skillset."""
        self._skillsets[skillset.skillset_name] = skillset

    def get_skillset(self, name: str = "standard_graph_skillset") -> Optional[GraphSkillset]:
        """Retrieve a registered graph skillset."""
        return self._skillsets.get(name)

    def list_skillsets(self) -> List[str]:
        """List registered skillset names."""
        return list(self._skillsets.keys())
