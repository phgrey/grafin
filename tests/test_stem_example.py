import pytest
from pathlib import Path
from graphin.config import AppConfig
from graphin.manifest.loader import load_manifest_from_yaml
from graphin.adapters.langgraph_adapter import LangGraphAdapter
from examples.stem_markdown_processor.utils.stem_taxonomy import validate_discipline
from examples.stem_markdown_processor.nodes.semantic_chunker import split_markdown_into_sections
from examples.stem_markdown_processor.nodes.stem_classifier import heuristic_fallback_classifier


def test_stem_example_taxonomy_validation():
    assert validate_discipline("Physics") is True
    assert validate_discipline("Quantum Mechanics") is True
    assert validate_discipline("Artificial Intelligence & Machine Learning") is True
    assert validate_discipline("Calculus & Analysis") is True


def test_stem_example_chunking():
    md = "# Section Title\n\nContent for section."
    chunks = split_markdown_into_sections("test.md", md)
    assert len(chunks) == 1
    assert chunks[0]["section_title"] == "Section Title"


def test_stem_example_full_pipeline(tmp_path):
    manifest_path = "examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml"
    manifest = load_manifest_from_yaml(manifest_path)

    source_dir = tmp_path / "source"
    output_dir = tmp_path / "results"
    source_dir.mkdir()

    sample_file = source_dir / "quantum_test.md"
    sample_file.write_text("# Quantum Physics\n\nSuperposition of qubits in quantum circuits.")

    cfg = AppConfig(
        source_dir=str(source_dir),
        output_dir=str(output_dir),
        confidence_threshold=0.70,
    )

    adapter = LangGraphAdapter()
    compiled_graph = adapter.build_executable(manifest)

    initial_state = {
        "config": cfg.model_dump(),
        "classified_chunks": [],
        "pending_reviews": [],
        "saved_results": [],
    }

    thread_config = {"configurable": {"thread_id": "test-stem-run"}}
    res_state = compiled_graph.invoke(initial_state, config=thread_config)

    saved_files = res_state.get("saved_results", [])
    assert len(saved_files) > 0
    assert (output_dir / "quantum_test_tagged.md").exists()
