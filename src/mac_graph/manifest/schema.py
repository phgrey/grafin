from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class NodeDefinition(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    type: str = Field(default="function", description="Node type: 'function', 'agent', 'tool', 'interrupt'")
    code_ref: str = Field(..., description="Python dot-notation code reference (e.g. module.path:function_name)")
    description: Optional[str] = Field(default="", description="Human readable node description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Framework-specific metadata")


class EdgeDefinition(BaseModel):
    source: str = Field(..., description="Source node ID or '__start__'")
    target: Optional[str] = Field(default=None, description="Target node ID or '__end__'")
    condition_ref: Optional[str] = Field(
        default=None, description="Python code reference for conditional routing function"
    )
    branches: Optional[Dict[str, str]] = Field(
        default=None, description="Mapping of branch key to target node ID for conditional edges"
    )


class GraphManifest(BaseModel):
    version: str = Field(default="0.1.0", description="Manifest format version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Graph metadata (name, description, author)")
    state_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for graph state")
    nodes: List[NodeDefinition] = Field(default_factory=list, description="List of node definitions")
    edges: List[EdgeDefinition] = Field(default_factory=list, description="List of edge definitions")
    framework_configs: Dict[str, Any] = Field(
        default_factory=dict, description="Framework-specific configuration blocks (langgraph, crewai, semantic_kernel)"
    )

    def get_node(self, node_id: str) -> Optional[NodeDefinition]:
        """Find a node definition by its ID."""
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def add_node(self, node: NodeDefinition) -> None:
        """Add or update a node in the manifest."""
        for i, n in enumerate(self.nodes):
            if n.id == node.id:
                self.nodes[i] = node
                return
        self.nodes.append(node)

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and its connected edges from the manifest."""
        initial_count = len(self.nodes)
        self.nodes = [n for n in self.nodes if n.id != node_id]
        if len(self.nodes) < initial_count:
            # Clean up connected edges
            self.edges = [
                e for e in self.edges
                if e.source != node_id and e.target != node_id and (not e.branches or node_id not in e.branches.values())
            ]
            return True
        return False
