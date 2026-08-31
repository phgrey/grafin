from typing import Dict, Any, List, Optional
from graphin.adapters.base import IFrameworkAdapter
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition
from graphin.cordis.context import Context, Service


class CordisNodeService(Service):
    """Cordis service wrapping a GraphIn node."""

    def __init__(self, ctx: Context, node_def: NodeDefinition):
        self.node_def = node_def
        self.service_name = f"node_{node_def.id}"
        super().__init__(ctx, name=self.service_name)
        self.state: Dict[str, Any] = {}

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        self.ctx.emit("cordis/node_before_execute", self.node_def.id, inputs)
        outputs = {"status": "executed", "node_id": self.node_def.id, "input_summary": list(inputs.keys())}
        self.ctx.emit("cordis/node_after_execute", self.node_def.id, outputs)
        return outputs


class CordisAdapter(IFrameworkAdapter):
    """Framework adapter converting GraphIn YAML manifests to Cordis microkernel plugin contexts."""

    def __init__(self):
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    @property
    def framework_name(self) -> str:
        return "cordis"

    def export_manifest(self, native_graph_obj: Any) -> GraphManifest:
        if isinstance(native_graph_obj, Context):
            nodes = []
            for name, service in native_graph_obj._services.items():
                if isinstance(service, CordisNodeService):
                    nodes.append(service.node_def)
            return GraphManifest(
                version="0.1.0",
                metadata={"name": "cordis_exported_graph"},
                nodes=nodes,
                edges=[],
                connections=[],
            )
        raise ValueError("native_graph_obj must be a Cordis Context instance")

    def build_executable(self, manifest: GraphManifest) -> Context:
        """Build a live Cordis Context executable from a GraphManifest."""
        ctx = Context()

        # Register nodes as Cordis services
        for node in manifest.nodes:
            node_service = CordisNodeService(ctx, node)
            # Register explicit execution handler plugin
            def make_plugin(n_def=node):
                def plugin_fn(c: Context):
                    def handle_run(node_id: str, inputs: Dict[str, Any]):
                        if node_id == n_def.id:
                            svc = c.get_service(f"node_{node_id}")
                            if svc:
                                return svc.execute(inputs)
                        return None
                    return c.on("cordis/run_node", handle_run)
                return plugin_fn

            ctx.plugin(make_plugin())

        return ctx

    def extract_config(self, manifest: GraphManifest) -> Dict[str, Any]:
        return manifest.metadata.get("cordis_config", {})

    def inject_config(self, manifest: GraphManifest, config_data: Dict[str, Any]) -> GraphManifest:
        manifest.metadata["cordis_config"] = config_data
        return manifest

    def manipulate_nodes_edges(
        self,
        manifest: GraphManifest,
        add_nodes: Optional[List[NodeDefinition]] = None,
        remove_nodes: Optional[List[str]] = None,
        add_edges: Optional[List[EdgeDefinition]] = None,
        remove_edges: Optional[List[EdgeDefinition]] = None,
    ) -> GraphManifest:
        if add_nodes:
            for n in add_nodes:
                manifest.add_node(n)
        if remove_nodes:
            for n_id in remove_nodes:
                manifest.remove_node(n_id)
        if add_edges:
            for e in add_edges:
                manifest.add_edge(e)
        if remove_edges:
            for e in remove_edges:
                manifest.remove_edge(e.source, e.target)
        return manifest

    def get_tool_wrapper(self) -> Any:
        def cordis_manipulate_tool(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success", "action": action, "payload": payload}
        return cordis_manipulate_tool

    def get_checkpoint_state(self, thread_id: str) -> Dict[str, Any]:
        return self._checkpoints.get(thread_id, {})

    def set_checkpoint_state(self, thread_id: str, state_data: Dict[str, Any]) -> None:
        self._checkpoints[thread_id] = state_data
