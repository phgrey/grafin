from typing import Dict, Any, List, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
try:
    from langgraph.types import interrupt
except ImportError:
    # Compatibility fallback if interrupt is imported differently
    def interrupt(val: Any) -> Any:
        return val

from mac_graph.state import GraphState, TextChunk
from mac_graph.nodes.document_loader import load_documents_node
from mac_graph.nodes.semantic_chunker import semantic_chunker_node
from mac_graph.nodes.stem_classifier import stem_classifier_node
from mac_graph.nodes.result_saver import save_results_node


def human_review_node(state: GraphState) -> Dict[str, Any]:
    """Node: Handles Human-In-The-Loop (HITL) interrupt when classification confidence is below threshold.
    
    If state contains pending_reviews, triggers interrupt to request user confirmation/override.
    When resumed with user_override input, updates the pending chunk and continues.
    """
    pending_reviews: List[TextChunk] = state.get("pending_reviews", [])
    classified_chunks: List[TextChunk] = list(state.get("classified_chunks", []))
    user_override = state.get("user_override")

    if not pending_reviews:
        return {"status_message": "No pending reviews."}

    target_chunk = pending_reviews[0]

    # If no user override provided in current state step, trigger LangGraph interrupt
    if not user_override:
        # Prompt value passed to interrupt caller
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
        # Interrupt graph execution and wait for user response
        user_response = interrupt(prompt_data)
        if isinstance(user_response, dict):
            user_override = user_response

    # Apply user override if received
    if user_override:
        new_domain = user_override.get("primary_domain", target_chunk.get("primary_domain"))
        new_discipline = user_override.get("discipline", target_chunk.get("discipline"))
        new_reasoning = user_override.get("reasoning", f"User confirmed/overrode tag to '{new_discipline}'.")

        updated_chunk: TextChunk = dict(target_chunk)  # type: ignore
        updated_chunk["primary_domain"] = new_domain
        updated_chunk["discipline"] = new_discipline
        updated_chunk["confidence_score"] = 1.0  # Set confidence to max upon manual verification
        updated_chunk["reasoning"] = new_reasoning
        updated_chunk["status"] = "verified"
        updated_chunk["human_verified"] = True

        # Update chunk in classified_chunks list
        for i, chk in enumerate(classified_chunks):
            if chk.get("id") == target_chunk.get("id"):
                classified_chunks[i] = updated_chunk
                break

        # Remove processed chunk from pending_reviews
        remaining_pending = pending_reviews[1:]

        return {
            "classified_chunks": classified_chunks,
            "pending_reviews": remaining_pending,
            "user_override": None,  # Reset override
            "status_message": f"Successfully verified chunk '{target_chunk.get('id')}' as '{new_discipline}'.",
        }

    return {}


def check_confidence_routing(state: GraphState) -> Literal["human_review", "save_results"]:
    """Conditional Edge: Determines whether to route to HITL review or proceed to saving results."""
    pending = state.get("pending_reviews", [])
    if len(pending) > 0:
        return "human_review"
    return "save_results"


def build_mac_graph(checkpointer: Any = None) -> StateGraph:
    """Build and compile the mac-graph execution workflow."""
    builder = StateGraph(GraphState)

    # Add nodes
    builder.add_node("load_documents", load_documents_node)
    builder.add_node("semantic_chunker", semantic_chunker_node)
    builder.add_node("stem_classifier", stem_classifier_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("save_results", save_results_node)

    # Add edges
    builder.add_edge(START, "load_documents")
    builder.add_edge("load_documents", "semantic_chunker")
    builder.add_edge("semantic_chunker", "stem_classifier")

    # Conditional routing after classification
    builder.add_conditional_edges(
        "stem_classifier",
        check_confidence_routing,
        {
            "human_review": "human_review",
            "save_results": "save_results",
        },
    )

    # Loop back from human review until pending list is cleared
    builder.add_conditional_edges(
        "human_review",
        check_confidence_routing,
        {
            "human_review": "human_review",
            "save_results": "save_results",
        },
    )

    builder.add_edge("save_results", END)

    if checkpointer is None:
        checkpointer = MemorySaver()

    return builder.compile(checkpointer=checkpointer)
