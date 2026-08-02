import json
from typing import Dict, Any, List, Optional


class AdaptiveCardGenerator:
    """Generates Microsoft Adaptive Card JSON schemas for centralized HITL review interrupts."""

    @staticmethod
    def create_hitl_review_card(
        chunk_id: str,
        section_title: str,
        source_file: str,
        suggested_domain: str,
        suggested_discipline: str,
        confidence_score: float,
        reasoning: str,
        snippet: str,
        available_taxonomy: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """Construct a structured v1.4 Adaptive Card JSON object for a low-confidence interrupt."""
        card_body = [
            {
                "type": "TextBlock",
                "text": "⚠️ STEM Classification HITL Interrupt",
                "weight": "Bolder",
                "size": "Large",
                "color": "Warning",
            },
            {
                "type": "TextBlock",
                "text": f"Graph execution paused due to low classification confidence ({confidence_score:.2f}).",
                "isSubtle": True,
                "wrap": True,
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Chunk ID:", "value": chunk_id},
                    {"title": "Source File:", "value": source_file},
                    {"title": "Section Title:", "value": section_title},
                    {"title": "Suggested Domain:", "value": suggested_domain},
                    {"title": "Suggested Tag:", "value": suggested_discipline},
                    {"title": "Confidence Score:", "value": f"{confidence_score:.2f}"},
                ],
            },
            {
                "type": "TextBlock",
                "text": f"**LLM Reasoning:** {reasoning}",
                "wrap": True,
            },
            {
                "type": "Container",
                "style": "emphasis",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "Text Content Snippet:",
                        "weight": "Bolder",
                    },
                    {
                        "type": "TextBlock",
                        "text": f"\"{snippet[:300]}...\"",
                        "wrap": True,
                        "fontType": "Monospace",
                        "size": "Small",
                    },
                ],
            },
        ]

        actions = [
            {
                "type": "Action.Submit",
                "title": f"✅ Confirm ('{suggested_discipline}')",
                "data": {
                    "action": "confirm",
                    "chunk_id": chunk_id,
                    "primary_domain": suggested_domain,
                    "discipline": suggested_discipline,
                },
            },
            {
                "type": "Action.Submit",
                "title": "✏️ Select from STEM Taxonomy",
                "data": {
                    "action": "select_taxonomy",
                    "chunk_id": chunk_id,
                },
            },
        ]

        return {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": card_body,
            "actions": actions,
        }

    @staticmethod
    def to_json_string(card_dict: Dict[str, Any]) -> str:
        """Render Adaptive Card dictionary to formatted JSON string."""
        return json.dumps(card_dict, indent=2)
