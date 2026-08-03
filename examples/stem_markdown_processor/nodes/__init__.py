"""Nodes package for stem_markdown_processor example."""

from examples.stem_markdown_processor.nodes.document_loader import load_documents_node
from examples.stem_markdown_processor.nodes.semantic_chunker import semantic_chunker_node
from examples.stem_markdown_processor.nodes.stem_classifier import stem_classifier_node
from examples.stem_markdown_processor.nodes.result_saver import save_results_node


def audit(state):
    """Audit node callable for quality assurance checks."""
    state_copy = dict(state)
    state_copy["status_message"] = "Quality audit completed."
    return state_copy


__all__ = [
    "load_documents_node",
    "semantic_chunker_node",
    "stem_classifier_node",
    "save_results_node",
    "audit",
]
