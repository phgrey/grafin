from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition


class GraphSkillset(ABC):
    """Abstract Skillset Protocol for inspecting, walking, and mutating graph topology & state across orchestrators."""

    @property
    @abstractmethod
    def skillset_name(self) -> str:
        """Name of the skillset implementation."""
        pass

    @abstractmethod
    def walk_topology(self, manifest: GraphManifest) -> Dict[str, Any]:
        """Walk manifest topology and return node/edge metadata."""
        pass

    @abstractmethod
    def get_node_details(self, manifest: GraphManifest, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve details of a specific node."""
        pass

    @abstractmethod
    def mutate_node(self, manifest: GraphManifest, node: NodeDefinition) -> bool:
        """Add or update a node in the manifest."""
        pass

    @abstractmethod
    def remove_node(self, manifest: GraphManifest, node_id: str) -> bool:
        """Remove a node from the manifest."""
        pass

    @abstractmethod
    def get_connections(self, manifest: GraphManifest) -> List[Dict[str, Any]]:
        """Retrieve shared connection access points."""
        pass
