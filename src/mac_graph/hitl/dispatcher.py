from typing import Dict, Any, Optional, Callable
from mac_graph.hitl.adaptive_card import AdaptiveCardGenerator


class HITLDispatcher:
    """Centralized dispatcher that formats graph interrupts into Adaptive Cards and sends messages to target conversations."""

    def __init__(self, message_sink: Optional[Callable[[Dict[str, Any], str], None]] = None):
        self.message_sink = message_sink or self._default_console_sink

    def _default_console_sink(self, card_payload: Dict[str, Any], card_json: str) -> None:
        """Default sink printing Adaptive Card payload to system log / conversation output."""
        print(f"\n[HITL DISPATCHER] Intercepted interrupt. Dispatching Adaptive Card JSON:\n{card_json}\n")

    def dispatch_interrupt(
        self,
        interrupt_data: Dict[str, Any],
        conversation_id: str = "sk_default_channel",
    ) -> Dict[str, Any]:
        """Convert raw graph interrupt payload into an Adaptive Card JSON payload and route to target conversation."""
        chunk_id = interrupt_data.get("chunk_id", "unknown_chunk")
        title = interrupt_data.get("section_title", "Untitled Section")
        src = interrupt_data.get("source_file", "unknown.md")
        suggested_domain = interrupt_data.get("suggested_primary_domain", interrupt_data.get("primary_domain", "Science"))
        suggested_disc = interrupt_data.get("suggested_discipline", interrupt_data.get("discipline", "Unclassified"))
        confidence = float(interrupt_data.get("confidence_score", 0.5))
        reasoning = interrupt_data.get("reasoning", "Low confidence requires user confirmation.")
        snippet = interrupt_data.get("content_snippet", interrupt_data.get("content", ""))

        card_dict = AdaptiveCardGenerator.create_hitl_review_card(
            chunk_id=chunk_id,
            section_title=title,
            source_file=src,
            suggested_domain=suggested_domain,
            suggested_discipline=suggested_disc,
            confidence_score=confidence,
            reasoning=reasoning,
            snippet=snippet,
        )

        card_json = AdaptiveCardGenerator.to_json_string(card_dict)

        # Dispatch payload to destination sink
        self.message_sink(card_dict, card_json)

        return {
            "status": "dispatched",
            "conversation_id": conversation_id,
            "card": card_dict,
        }
