import json
from typing import Dict, Any, List, Optional
from graphin.adapters.base import IFrameworkAdapter
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition, ModelDefinition
from graphin.llm import resolve_api_key


class SemanticKernelFunctionFilter:
    """Execution filter for Semantic Kernel to intercept plugin function calls and enforce ACL rules."""

    def __init__(self, allowed_actions: Optional[List[str]] = None):
        self.allowed_actions = allowed_actions or ["add_node", "remove_node", "add_edge", "inspect_graph"]

    def on_function_invoking(self, function_name: str, kwargs: Dict[str, Any]) -> bool:
        action = kwargs.get("action", function_name)
        if action not in self.allowed_actions:
            print(f"SK Filter ACL BLOCKED: Action '{action}' is not in allowed_actions.")
            return False
        return True


class GraphManipulationPlugin:
    """Semantic Kernel Plugin exposing graph manifest manipulation tools to chat assistants and planners."""

    def __init__(self, adapter: "SemanticKernelAdapter", manifest: GraphManifest):
        self.adapter = adapter
        self.manifest = manifest

    def manipulate_graph(
        self,
        action: str,
        node_id: Optional[str] = None,
        node_type: Optional[str] = "function",
        code_ref: Optional[str] = None,
        source_edge: Optional[str] = None,
        target_edge: Optional[str] = None,
    ) -> str:
        if not self.adapter.filter.on_function_invoking("manipulate_graph", {"action": action}):
            return f"ACL_DENIED: Action '{action}' blocked by Semantic Kernel Filter."

        if action == "add_node" and node_id and code_ref:
            new_node = NodeDefinition(id=node_id, type=node_type or "function", code_ref=code_ref)
            self.adapter.manipulate_nodes_edges(self.manifest, add_nodes=[new_node])
            return f"SUCCESS: Semantic Kernel added node '{node_id}'."

        elif action == "remove_node" and node_id:
            success = self.manifest.remove_node(node_id)
            if success:
                return f"SUCCESS: Semantic Kernel removed node '{node_id}'."
            return f"WARNING: Node '{node_id}' not found."

        elif action == "inspect_graph":
            return json.dumps(self.manifest.model_dump(), indent=2)

        return f"INVALID_ACTION: '{action}'."


class SemanticKernelAdapter(IFrameworkAdapter):
    """Semantic Kernel Framework Adapter (Backend): Enables dynamic AI reasoning & discussion over graph manifest."""

    def __init__(self, filter_allowed_actions: Optional[List[str]] = None):
        self.filter = SemanticKernelFunctionFilter(allowed_actions=filter_allowed_actions)
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    @property
    def framework_name(self) -> str:
        return "semantic_kernel"

    def extract_config(self, manifest: GraphManifest) -> Dict[str, Any]:
        base_cfg = dict(manifest.framework_configs.get("semantic_kernel", {}))
        # Adopt manifest models into Semantic Kernel AI ChatCompletion service registries
        sk_services = {}
        for m in manifest.models:
            key = resolve_api_key(m.api_key_env, provider=m.provider)
            sk_services[m.id] = {
                "service_id": m.id,
                "ai_model_id": m.model_name,
                "provider": m.provider,
                "endpoint": m.endpoint,
                "protocol": m.protocol,
                "api_key": key,
                "parameters": m.parameters,
            }
        base_cfg["ai_services"] = sk_services
        return base_cfg

    def inject_config(self, manifest: GraphManifest, config_data: Dict[str, Any]) -> GraphManifest:
        manifest.framework_configs["semantic_kernel"] = config_data
        return manifest

    def build_executable(self, manifest: GraphManifest) -> Dict[str, Any]:
        plugins = {}
        for node in manifest.nodes:
            plugins[node.id] = {
                "name": node.id,
                "description": node.description,
                "code_ref": node.code_ref,
            }

        sk_config = self.extract_config(manifest)

        return {
            "kernel_service_id": sk_config.get("service_id", "default"),
            "ai_services": sk_config.get("ai_services", {}),
            "plugins": plugins,
            "edges": [e.model_dump() for e in manifest.edges],
        }

    def export_manifest(self, native_graph_obj: Any) -> GraphManifest:
        if isinstance(native_graph_obj, GraphManifest):
            return native_graph_obj

        nodes = []
        models = []
        if isinstance(native_graph_obj, dict):
            if "plugins" in native_graph_obj:
                for name, spec in native_graph_obj["plugins"].items():
                    nodes.append(
                        NodeDefinition(
                            id=name,
                            type="function",
                            code_ref=spec.get("code_ref", f"sk_plugin:{name}"),
                            description=spec.get("description", ""),
                        )
                    )
            if "ai_services" in native_graph_obj:
                for sid, s_spec in native_graph_obj["ai_services"].items():
                    models.append(
                        ModelDefinition(
                            id=sid,
                            provider=s_spec.get("provider", "gemini"),
                            model_name=s_spec.get("ai_model_id", "default"),
                            endpoint=s_spec.get("endpoint"),
                            protocol=s_spec.get("protocol", "https"),
                            parameters=s_spec.get("parameters", {}),
                        )
                    )

        return GraphManifest(
            version="0.1.0",
            metadata={"name": "exported_sk_kernel"},
            models=models,
            nodes=nodes,
            framework_configs={"semantic_kernel": {"exported": True}},
        )

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

    def get_tool_wrapper(self, manifest: Optional[GraphManifest] = None) -> GraphManipulationPlugin:
        dummy_manifest = manifest or GraphManifest(version="0.1.0")
        return GraphManipulationPlugin(self, dummy_manifest)

    def get_checkpoint_state(self, thread_id: str) -> Dict[str, Any]:
        return self._checkpoints.get(thread_id, {})

    def set_checkpoint_state(self, thread_id: str, state_data: Dict[str, Any]) -> None:
        self._checkpoints[thread_id] = state_data
