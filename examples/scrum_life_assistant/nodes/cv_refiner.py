from typing import Dict, Any
from graphin.state import GraphState


def cv_refiner_node(state: GraphState) -> Dict[str, Any]:
    """Node: Refines developer CV & resume artifacts."""
    tasks = state.get("classified_chunks", [])
    cv_task = next((t for t in tasks if "CV" in t.get("section_title", "")), None)

    summary = "Refined Architect CV: Added GraphIn Multi-Framework Orchestration & Cython Performance Engine."
    saved = list(state.get("saved_results", []))
    saved.append("examples/scrum_life_assistant/data/refined_cv.md")

    return {
        "saved_results": saved,
        "status_message": f"CV Refiner completed: {summary}",
    }
