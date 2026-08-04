from typing import Dict, Any, List
from graphin.state import GraphState


def sprint_planner_node(state: GraphState) -> Dict[str, Any]:
    """Node: Plans SCRUM sprint backlog combining work features and side life tasks."""
    sprint_backlog = [
        {"section_title": "Sprint Task 1: Refine Software Architect CV", "content": "Update resume with GraphIn experience", "priority": "high"},
        {"section_title": "Sprint Task 2: Monthly Budget Audit", "content": "Review cloud infrastructure costs and expenses", "priority": "medium"},
        {"section_title": "Incident Task: Doctor Appointment Reminder", "content": "Schedule annual health checkup", "priority": "high", "schedule": "0 9 * * *"},
    ]

    return {
        "classified_chunks": sprint_backlog,
        "pending_reviews": [],
        "status_message": f"SCRUM Sprint Planner created {len(sprint_backlog)} tasks in backlog.",
    }
