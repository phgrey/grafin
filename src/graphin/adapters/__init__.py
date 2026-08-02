"""Framework Adapters for LangGraph, CrewAI, Semantic Kernel, and GraphInYAML."""

from graphin.adapters.base import IFrameworkAdapter
from graphin.adapters.graphin_yaml_adapter import GraphInYAMLAdapter
from graphin.adapters.langgraph_adapter import LangGraphAdapter
from graphin.adapters.crewai_adapter import CrewAIAdapter
from graphin.adapters.semantic_kernel_adapter import SemanticKernelAdapter

__all__ = [
    "IFrameworkAdapter",
    "GraphInYAMLAdapter",
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
    elif name_lower in ("graphin_yaml", "graphinyaml", "yamlgraph"):
        return GraphInYAMLAdapter()
    else:
        raise ValueError(f"Unknown adapter name: '{name}'. Available: langgraph, crewai, semantic_kernel, graphin_yaml.")
