import os
import shutil
import pytest
from pathlib import Path

from mac_graph.config import AppConfig
from mac_graph.nodes.document_loader import load_documents_node
from mac_graph.nodes.semantic_chunker import split_markdown_into_sections, semantic_chunker_node
from mac_graph.nodes.stem_classifier import stem_classifier_node, heuristic_fallback_classifier
from mac_graph.nodes.result_saver import save_results_node
from mac_graph.utils.stem_taxonomy import validate_discipline, get_all_disciplines
from mac_graph.graph import build_mac_graph
from langgraph.checkpoint.memory import MemorySaver


def test_stem_taxonomy_validation():
    assert validate_discipline("Physics") is True
    assert validate_discipline("Quantum Mechanics") is True
    assert validate_discipline("Artificial Intelligence & Machine Learning") is True
    assert validate_discipline("Calculus & Analysis") is True
    assert validate_discipline("Biological Nonexistent Field 99") is False


def test_markdown_semantic_chunking():
    md_content = """# Title Heading

## Section 1
Content of section 1 with quantum physics.

## Section 2
Content of section 2 with calculus equations.
"""
    chunks = split_markdown_into_sections("test.md", md_content)
    assert len(chunks) == 2
    assert chunks[0]["section_title"] == "Section 1"
    assert chunks[1]["section_title"] == "Section 2"


def test_heuristic_classifier():
    res_quantum = heuristic_fallback_classifier("Quantum", "Qubits and superposition")
    assert res_quantum.primary_domain == "Science"
    assert res_quantum.discipline == "Quantum Mechanics"
    assert res_quantum.confidence_score >= 0.8

    res_ambiguous = heuristic_fallback_classifier("Generic", "Some random text without clear keywords")
    assert res_ambiguous.confidence_score < 0.75


def test_full_graph_execution_pipeline(tmp_path):
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "results"
    source_dir.mkdir()

    # Create sample file
    sample_file = source_dir / "sample.md"
    sample_file.write_text("""# Quantum Notes

## Quantum Mechanics
Study of particles and superposition principles.

## Calculus Derivatives
Study of differential equations and limits.
""")

    cfg = AppConfig(
        source_dir=str(source_dir),
        output_dir=str(output_dir),
        confidence_threshold=0.70,
        provider="gemini",
    )

    checkpointer = MemorySaver()
    compiled_graph = build_mac_graph(checkpointer=checkpointer)

    initial_state = {
        "config": cfg.model_dump(),
        "classified_chunks": [],
        "pending_reviews": [],
        "saved_results": [],
    }

    thread_config = {"configurable": {"thread_id": "test-run"}}
    res_state = compiled_graph.invoke(initial_state, config=thread_config)

    # Check results
    saved_files = res_state.get("saved_results", [])
    assert len(saved_files) > 0
    assert (output_dir / "sample_tagged.md").exists()
    assert (output_dir / "classification_summary.json").exists()
