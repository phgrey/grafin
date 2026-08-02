import json
import pytest
from mac_graph.hitl.adaptive_card import AdaptiveCardGenerator
from mac_graph.hitl.dispatcher import HITLDispatcher


def test_adaptive_card_generator():
    card_dict = AdaptiveCardGenerator.create_hitl_review_card(
        chunk_id="chunk_101",
        section_title="Quantum Superposition",
        source_file="01_quantum.md",
        suggested_domain="Science",
        suggested_discipline="Quantum Mechanics",
        confidence_score=0.55,
        reasoning="Low confidence due to ambiguous terms.",
        snippet="Quantum computing leverages superposition...",
    )

    assert card_dict["$schema"] == "http://adaptivecards.io/schemas/adaptive-card.json"
    assert card_dict["type"] == "AdaptiveCard"
    assert card_dict["version"] == "1.4"
    assert len(card_dict["actions"]) == 2

    json_str = AdaptiveCardGenerator.to_json_string(card_dict)
    parsed = json.loads(json_str)
    assert parsed["type"] == "AdaptiveCard"


def test_hitl_dispatcher():
    dispatched_cards = []

    def mock_sink(card_dict, card_json):
        dispatched_cards.append((card_dict, card_json))

    dispatcher = HITLDispatcher(message_sink=mock_sink)

    interrupt_data = {
        "chunk_id": "chunk_999",
        "section_title": "Deep Learning Models",
        "source_file": "02_deep.md",
        "primary_domain": "Technology",
        "discipline": "Artificial Intelligence & Machine Learning",
        "confidence_score": 0.60,
        "reasoning": "Needs human verification.",
        "content": "Neural network optimization...",
    }

    res = dispatcher.dispatch_interrupt(interrupt_data, conversation_id="sk_channel_123")
    assert res["status"] == "dispatched"
    assert res["conversation_id"] == "sk_channel_123"

    assert len(dispatched_cards) == 1
    card_dict, card_json = dispatched_cards[0]
    assert card_dict["type"] == "AdaptiveCard"
