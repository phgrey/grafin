import os
import sys
from typing import Dict, Any

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from graphin.state import GraphState
from graphin.config import AppConfig
from examples.stem_markdown_processor.phase1_langgraph_export_and_run import run_phase_1


def stem_processor_subgraph_node(state: GraphState) -> Dict[str, Any]:
    """LangGraph Sub-Graph Node Callable: Imports and executes Example #1 (STEM Markdown Processor) as a sub-workflow."""
    # Execute Example #1 STEM processor workflow
    stem_manifest = run_phase_1(interactive=False)

    saved = list(state.get("saved_results", []))
    saved.append("examples/stem_markdown_processor/data/results/summary_report.json")

    return {
        "saved_results": saved,
        "status_message": f"Sub-Graph Execution Complete: Embedded STEM Markdown Processor workflow ('{stem_manifest.metadata.get('name')}') executed successfully.",
        "stem_subgraph_info": {
            "manifest_name": stem_manifest.metadata.get("name"),
            "node_count": len(stem_manifest.nodes),
            "status": "completed",
        },
    }
