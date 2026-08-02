"""Framework Adapters for LangGraph, CrewAI, Semantic Kernel, and YamlGraph."""

from mac_graph.adapters.base import IFrameworkAdapter
from mac_graph.adapters.yamlgraph_adapter import YamlGraphAdapter
from mac_graph.adapters.langgraph_adapter import LangGraphAdapter
from mac_graph.adapters.crewai_adapter import CrewAIAdapter
from mac_graph.adapters.semantic_kernel_adapter import SemanticKernelAdapter

__all__ = [
    "IFrameworkAdapter",
    "YamlGraphAdapter",
    "LangGraphAdapter",
    "CrewAIAdapter",
    "SemanticKernelAdapter",
    "get_adapter_by_name",
]


def get_adapter_by_name(name: str) -> IFrameworkAdapter:
    """Retrieve adapter instance by name."""
    name_lower = name.lower().strip()
    if name_lower == "langgraph":
        return LangGraphAdapter()
    elif name_lower == "crewai":
        return CrewAIAdapter()
    elif name_lower in ("semantic_kernel", "semantickernel", "sk"):
        return SemanticKernelAdapter()
    elif name_lower == "yamlgraph":
        return YamlGraphAdapter()
    else:
        raise ValueError(f"Unknown adapter name: '{name}'. Available: langgraph, crewai, semantic_kernel, yamlgraph.")
