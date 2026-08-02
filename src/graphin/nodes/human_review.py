from typing import Dict, Any, List
from graphin.state import GraphState, TextChunk

try:
    from langgraph.types import interrupt
except ImportError:
    def interrupt(val: Any) -> Any:
        return val


def human_review_node(state: GraphState) -> Dict[str, Any]:
    """Node: Handles Human-In-The-Loop (HITL) interrupt when classification confidence is below threshold."""
    pending_reviews: List[TextChunk] = state.get("pending_reviews", [])
    classified_chunks: List[TextChunk] = list(state.get("classified_chunks", []))
    user_override = state.get("user_override")

    if not pending_reviews:
        return {"status_message": "No pending reviews."}

    target_chunk = pending_reviews[0]

    if not user_override:
        prompt_data = {
            "chunk_id": target_chunk.get("id"),
            "section_title": target_chunk.get("section_title"),
            "source_file": target_chunk.get("source_file"),
            "suggested_primary_domain": target_chunk.get("primary_domain"),
            "suggested_discipline": target_chunk.get("discipline"),
            "confidence_score": target_chunk.get("confidence_score"),
            "reasoning": target_chunk.get("reasoning"),
            "content_snippet": target_chunk.get("content", "")[:300],
        }
        user_response = interrupt(prompt_data)
        if isinstance(user_response, dict):
            user_override = user_response

    if user_override:
        new_domain = user_override.get("primary_domain", target_chunk.get("primary_domain"))
        new_discipline = user_override.get("discipline", target_chunk.get("discipline"))
        new_reasoning = user_override.get("reasoning", f"User confirmed/overrode tag to '{new_discipline}'.")

        updated_chunk: TextChunk = dict(target_chunk)  # type: ignore
        updated_chunk["primary_domain"] = new_domain
        updated_chunk["discipline"] = new_discipline
        updated_chunk["confidence_score"] = 1.0
        updated_chunk["reasoning"] = new_reasoning
        updated_chunk["status"] = "verified"
        updated_chunk["human_verified"] = True

        for i, chk in enumerate(classified_chunks):
            if chk.get("id") == target_chunk.get("id"):
                classified_chunks[i] = updated_chunk
                break

        remaining_pending = pending_reviews[1:]

        return {
            "classified_chunks": classified_chunks,
            "pending_reviews": remaining_pending,
            "user_override": None,
            "status_message": f"Successfully verified chunk '{target_chunk.get('id')}' as '{new_discipline}'.",
        }

    return {}
