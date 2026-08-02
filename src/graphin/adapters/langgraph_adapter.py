import os
import sys
import importlib
from typing import Dict, Any, List, Optional, Callable
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from graphin.adapters.base import IFrameworkAdapter
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition
from graphin.state import GraphState


def resolve_code_ref(code_ref: str) -> Callable:
    """Dynamically import a Python function or node callable from a code reference string (e.g. 'module.path:func_name')."""
    # Ensure current working directory is in sys.path to resolve local project references
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    if ":" in code_ref:
        module_path, attr_name = code_ref.split(":", 1)
    elif "." in code_ref:
        module_path, attr_name = code_ref.rsplit(".", 1)
    else:
        raise ValueError(f"Invalid code reference format '{code_ref}'. Must be 'module.path:attribute'.")

    module = importlib.import_module(module_path)
    if not hasattr(module, attr_name):
        raise AttributeError(f"Module '{module_path}' has no attribute '{attr_name}'.")

    return getattr(module, attr_name)


class LangGraphAdapter(IFrameworkAdapter):
    """LangGraph Framework Adapter: Constructs, exports, and manipulates LangGraph StateGraphs from GraphManifest."""

    def __init__(self, checkpointer: Optional[Any] = None):
        self.checkpointer = checkpointer or MemorySaver()
        self._compiled_graphs: Dict[str, Any] = {}

    @property
    def framework_name(self) -> str:
        return "langgraph"

    def extract_config(self, manifest: GraphManifest) -> Dict[str, Any]:
        return manifest.framework_configs.get("langgraph", {})

    def inject_config(self, manifest: GraphManifest, config_data: Dict[str, Any]) -> GraphManifest:
        manifest.framework_configs["langgraph"] = config_data
        return manifest

    def build_executable(self, manifest: GraphManifest) -> StateGraph:
        """Dynamically assemble a LangGraph StateGraph from the GraphManifest definition."""
        builder = StateGraph(GraphState)

        # 1. Add Nodes
        for node_def in manifest.nodes:
            fn_callable = resolve_code_ref(node_def.code_ref)
            builder.add_node(node_def.id, fn_callable)

        # 2. Add Edges
        for edge_def in manifest.edges:
            src = START if edge_def.source == "__start__" else edge_def.source
            tgt = END if edge_def.target == "__end__" else edge_def.target

            if edge_def.condition_ref and edge_def.branches:
                cond_fn = resolve_code_ref(edge_def.condition_ref)
                mapped_branches = {
                    k: (END if v == "__end__" else v) for k, v in edge_def.branches.items()
                }
                builder.add_conditional_edges(src, cond_fn, mapped_branches)
            elif tgt:
                builder.add_edge(src, tgt)

        compiled = builder.compile(checkpointer=self.checkpointer)
        manifest_name = manifest.metadata.get("name", "default_graph")
        self._compiled_graphs[manifest_name] = compiled
        return compiled

    def export_manifest(self, native_graph_obj: Any) -> GraphManifest:
        """Export a compiled StateGraph or builder instance back into a unified GraphManifest."""
        nodes: List[NodeDefinition] = []
        edges: List[EdgeDefinition] = []

        builder = getattr(native_graph_obj, "builder", native_graph_obj)

        if hasattr(builder, "nodes"):
            for node_id, node_spec in builder.nodes.items():
                if node_id in ("__start__", "__end__"):
                    continue
                func = getattr(node_spec, "func", str(node_spec))
                func_name = getattr(func, "__name__", str(func))
                func_mod = getattr(func, "__module__", "graphin")
                code_ref = f"{func_mod}:{func_name}"

                nodes.append(
                    NodeDefinition(
                        id=node_id,
                        type="function",
                        code_ref=code_ref,
                        description=f"Exported node {node_id}",
                    )
                )

        return GraphManifest(
            version="0.1.0",
            metadata={"name": "exported_langgraph", "description": "Exported from compiled LangGraph"},
            nodes=nodes,
            edges=edges,
            framework_configs={"langgraph": {"exported": True}},
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

    def get_tool_wrapper(self) -> Any:
        return self.manipulate_nodes_edges

    def get_checkpoint_state(self, thread_id: str) -> Dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id}}
        state = self.checkpointer.get(config)
        return dict(state) if state else {}

    def set_checkpoint_state(self, thread_id: str, state_data: Dict[str, Any]) -> None:
        config = {"configurable": {"thread_id": thread_id}}
        self.checkpointer.put(config, state_data)
