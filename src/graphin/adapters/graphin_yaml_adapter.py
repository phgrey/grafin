from typing import Dict, Any, List, Optional
from graphin.adapters.base import IFrameworkAdapter
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition
from graphin.manifest.loader import save_manifest_to_yaml, load_manifest_from_yaml


class GraphInYAMLAdapter(IFrameworkAdapter):
    """Native GraphInYAML Adapter for direct manifest manipulation and storage."""

    def __init__(self):
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    @property
    def framework_name(self) -> str:
        return "graphin_yaml"

    def export_manifest(self, native_graph_obj: Any) -> GraphManifest:
        if isinstance(native_graph_obj, GraphManifest):
            return native_graph_obj
        elif isinstance(native_graph_obj, (str, dict)):
            if isinstance(native_graph_obj, dict):
                return GraphManifest(**native_graph_obj)
            return load_manifest_from_yaml(native_graph_obj)
        raise ValueError("Cannot export native_graph_obj to GraphInYAML manifest.")

    def build_executable(self, manifest: GraphManifest) -> GraphManifest:
        return manifest

    def extract_config(self, manifest: GraphManifest) -> Dict[str, Any]:
        return manifest.framework_configs.get("graphin_yaml", {})

    def inject_config(self, manifest: GraphManifest, config_data: Dict[str, Any]) -> GraphManifest:
        manifest.framework_configs["graphin_yaml"] = config_data
        return manifest

    def manipulate_nodes_edges(
        self,
        manifest: GraphManifest,
        add_nodes: Optional[List[NodeDefinition]] = None,
        remove_nodes: Optional[List[str]] = None,
        add_edges: Optional[List[EdgeDefinition]] = None,
        remove_edges: Optional[List[EdgeDefinition]] = None,
    ) -> GraphManifest:
        if remove_nodes:
            for nid in remove_nodes:
                manifest.remove_node(nid)

        if add_nodes:
            for node in add_nodes:
                manifest.add_node(node)

        if add_edges:
            for edge in add_edges:
                manifest.edges.append(edge)

        if remove_edges:
            for re in remove_edges:
                manifest.edges = [
                    e for e in manifest.edges
                    if not (e.source == re.source and e.target == re.target)
                ]

        return manifest

    def get_tool_wrapper(self) -> Any:
        return self.manipulate_nodes_edges

    def get_checkpoint_state(self, thread_id: str) -> Dict[str, Any]:
        return self._checkpoints.get(thread_id, {})

    def set_checkpoint_state(self, thread_id: str, state_data: Dict[str, Any]) -> None:
        self._checkpoints[thread_id] = state_data
