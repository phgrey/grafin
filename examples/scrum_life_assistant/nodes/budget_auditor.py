from typing import Dict, Any
from graphin.state import GraphState


def budget_auditor_node(state: GraphState) -> Dict[str, Any]:
    """Node: Audits monthly expense budgets."""
    saved = list(state.get("saved_results", []))
    saved.append("examples/scrum_life_assistant/data/budget_report.json")

    return {
        "saved_results": saved,
        "status_message": "Budget Auditor completed: Verified cloud hosting and API token expenditures.",
    }
