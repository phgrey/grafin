from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from mac_graph.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition


class IFrameworkAdapter(ABC):
    """Abstract Base Interface for framework-specific adapters (LangGraph, CrewAI, Semantic Kernel, YamlGraph)."""

    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Return the target framework identifier (e.g. 'langgraph', 'crewai', 'semantic_kernel', 'yamlgraph')."""
        pass

    @abstractmethod
    def export_manifest(self, native_graph_obj: Any) -> GraphManifest:
        """Export native framework object or definition to a unified GraphManifest."""
        pass

    @abstractmethod
    def build_executable(self, manifest: GraphManifest) -> Any:
        """Build native executable workflow object from a unified GraphManifest."""
        pass

    @abstractmethod
    def extract_config(self, manifest: GraphManifest) -> Dict[str, Any]:
        """Extract framework-specific configuration block from the manifest."""
        pass

    @abstractmethod
    def inject_config(self, manifest: GraphManifest, config_data: Dict[str, Any]) -> GraphManifest:
        """Inject updated framework-specific configuration block into the manifest."""
        pass

    @abstractmethod
    def manipulate_nodes_edges(
        self,
        manifest: GraphManifest,
        add_nodes: Optional[List[NodeDefinition]] = None,
        remove_nodes: Optional[List[str]] = None,
        add_edges: Optional[List[EdgeDefinition]] = None,
        remove_edges: Optional[List[EdgeDefinition]] = None,
    ) -> GraphManifest:
        """Dynamically add or remove nodes and edges from the manifest."""
        pass

    @abstractmethod
    def get_tool_wrapper(self) -> Any:
        """Expose manipulate_nodes_edges as a framework-native tool or plugin (e.g., CrewAI Tool or SK Plugin)."""
        pass

    @abstractmethod
    def get_checkpoint_state(self, thread_id: str) -> Dict[str, Any]:
        """Retrieve node/execution checkpoint state for a thread."""
        pass

    @abstractmethod
    def set_checkpoint_state(self, thread_id: str, state_data: Dict[str, Any]) -> None:
        """Update node/execution checkpoint state for a thread."""
        pass
