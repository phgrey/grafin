import json
from typing import Dict, Any, List, Optional, Callable
from graphin.adapters.base import IFrameworkAdapter
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition, ModelDefinition
from graphin.llm import resolve_api_key


class CrewAIGraphManipulationTool:
    """Tool wrapper exposing manifest node/edge manipulation for CrewAI agents."""

    def __init__(self, adapter: "CrewAIAdapter", manifest: GraphManifest):
        self.adapter = adapter
        self.manifest = manifest
        self.name = "manipulate_nodes_edges"
        self.description = (
            "Manipulate graph manifest nodes and edges dynamically. "
            "Use this tool to add new nodes, remove nodes, or reconfigure execution edges."
        )

    def _run(
        self,
        action: str,
        node_id: Optional[str] = None,
        node_type: Optional[str] = "function",
        code_ref: Optional[str] = None,
        source_edge: Optional[str] = None,
        target_edge: Optional[str] = None,
        agent_role: str = "agent",
    ) -> str:
        """Execute manifest mutation action with CrewAI ACL hook checks."""
        acl_allowed = self.adapter.check_acl(
            agent_role=agent_role, action=action, node_id=node_id, manifest=self.manifest
        )
        if not acl_allowed:
            return f"ACL DENIED: Agent role '{agent_role}' is not authorized to perform '{action}' on node '{node_id}'."

        if action == "add_node" and node_id and code_ref:
            new_node = NodeDefinition(id=node_id, type=node_type or "function", code_ref=code_ref)
            self.adapter.manipulate_nodes_edges(self.manifest, add_nodes=[new_node])
            return f"SUCCESS: Added node '{node_id}' with code_ref '{code_ref}' to graph manifest."

        elif action == "remove_node" and node_id:
            success = self.manifest.remove_node(node_id)
            if success:
                return f"SUCCESS: Removed node '{node_id}' from graph manifest."
            return f"WARNING: Node '{node_id}' not found in manifest."

        elif action == "add_edge" and source_edge and target_edge:
            new_edge = EdgeDefinition(source=source_edge, target=target_edge)
            self.adapter.manipulate_nodes_edges(self.manifest, add_edges=[new_edge])
            return f"SUCCESS: Added edge from '{source_edge}' to '{target_edge}'."

        return f"INVALID_ACTION: Unrecognized action '{action}'."


class CrewAIAdapter(IFrameworkAdapter):
    """CrewAI Framework Adapter (Frontend+): Translates manifest to CrewAI workflows, model configs, and ACL hooks."""

    def __init__(self, acl_policy: Optional[str] = "admin_only_node_deletion"):
        self.acl_policy = acl_policy
        self.before_hooks: List[Callable] = []
        self.after_hooks: List[Callable] = []
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    @property
    def framework_name(self) -> str:
        return "crewai"

    def register_before_hook(self, hook_fn: Callable) -> None:
        self.before_hooks.append(hook_fn)

    def register_after_hook(self, hook_fn: Callable) -> None:
        self.after_hooks.append(hook_fn)

    def check_acl(self, agent_role: str, action: str, node_id: Optional[str], manifest: GraphManifest) -> bool:
        if self.acl_policy == "admin_only_node_deletion":
            if action == "remove_node" and agent_role.lower() != "admin":
                return False
        return True

    def extract_config(self, manifest: GraphManifest) -> Dict[str, Any]:
        base_cfg = dict(manifest.framework_configs.get("crewai", {}))
        # Adopt manifest models into CrewAI LLM configurations
        llm_configs = {}
        for m in manifest.models:
            key = resolve_api_key(m.api_key_env, provider=m.provider)
            llm_configs[m.id] = {
                "model": f"{m.provider}/{m.model_name}",
                "base_url": m.endpoint,
                "protocol": m.protocol,
                "api_key": key,
                "parameters": m.parameters,
            }
        base_cfg["models"] = llm_configs
        return base_cfg

    def inject_config(self, manifest: GraphManifest, config_data: Dict[str, Any]) -> GraphManifest:
        manifest.framework_configs["crewai"] = config_data
        return manifest

    def build_executable(self, manifest: GraphManifest) -> Dict[str, Any]:
        tasks = []
        for node in manifest.nodes:
            tasks.append({
                "name": node.id,
                "description": node.description,
                "agent_role": "Specialist Agent",
                "code_ref": node.code_ref,
            })

        crewai_models = self.extract_config(manifest).get("models", {})

        return {
            "crew_name": manifest.metadata.get("name", "GraphIn_Crew"),
            "process": manifest.framework_configs.get("crewai", {}).get("process", "sequential"),
            "tasks": tasks,
            "crewai_llm_configs": crewai_models,
        }

    def export_manifest(self, native_graph_obj: Any) -> GraphManifest:
        if isinstance(native_graph_obj, GraphManifest):
            return native_graph_obj

        nodes = []
        models = []
        if isinstance(native_graph_obj, dict):
            if "tasks" in native_graph_obj:
                for task in native_graph_obj["tasks"]:
                    nodes.append(
                        NodeDefinition(
                            id=task["name"],
                            type="agent",
                            code_ref=task.get("code_ref", "graphin.nodes:default"),
                            description=task.get("description", ""),
                        )
                    )
            if "crewai_llm_configs" in native_graph_obj:
                for alias, cfg in native_graph_obj["crewai_llm_configs"].items():
                    prov, name = cfg["model"].split("/", 1) if "/" in cfg["model"] else ("gemini", cfg["model"])
                    models.append(
                        ModelDefinition(
                            id=alias,
                            provider=prov,
                            model_name=name,
                            endpoint=cfg.get("base_url"),
                            protocol=cfg.get("protocol", "https"),
                            parameters=cfg.get("parameters", {}),
                        )
                    )

        return GraphManifest(
            version="0.1.0",
            metadata={"name": native_graph_obj.get("crew_name", "exported_crew") if isinstance(native_graph_obj, dict) else "exported_crew"},
            models=models,
            nodes=nodes,
            framework_configs={"crewai": {"exported": True}},
        )

    def manipulate_nodes_edges(
        self,
        manifest: GraphManifest,
        add_nodes: Optional[List[NodeDefinition]] = None,
        remove_nodes: Optional[List[str]] = None,
        add_edges: Optional[List[EdgeDefinition]] = None,
        remove_edges: Optional[List[EdgeDefinition]] = None,
    ) -> GraphManifest:
        for hook in self.before_hooks:
            hook("manipulate_nodes_edges", manifest)

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

        for hook in self.after_hooks:
            hook("manipulate_nodes_edges", manifest)

        return manifest

    def get_tool_wrapper(self, manifest: Optional[GraphManifest] = None) -> CrewAIGraphManipulationTool:
        dummy_manifest = manifest or GraphManifest(version="0.1.0")
        return CrewAIGraphManipulationTool(self, dummy_manifest)

    def get_checkpoint_state(self, thread_id: str) -> Dict[str, Any]:
        return self._checkpoints.get(thread_id, {})

    def set_checkpoint_state(self, thread_id: str, state_data: Dict[str, Any]) -> None:
        self._checkpoints[thread_id] = state_data
