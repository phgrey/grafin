import os
import pytest
from pathlib import Path

# Enable GraphIn offline test mode to bypass live network API socket calls
os.environ["GRAPHIN_TEST_MODE"] = "1"

from graphin.config import AppConfig
from graphin.manifest.loader import load_manifest_from_yaml
from graphin.adapters.langgraph_adapter import LangGraphAdapter
from examples.stem_markdown_processor.utils.stem_taxonomy import validate_discipline
from examples.stem_markdown_processor.nodes.semantic_chunker import split_markdown_into_sections
from examples.stem_markdown_processor.phase1_langgraph_export_and_run import run_phase_1
from examples.stem_markdown_processor.phase2_crewai_inject_and_run import run_phase_2
from examples.stem_markdown_processor.phase3_semantic_kernel_inspect import run_phase_3


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


def test_single_orchestrator_experiment_phases():
    manifest1 = run_phase_1(interactive=False)
    assert manifest1 is not None
    assert len(manifest1.nodes) >= 5
    assert len(manifest1.models) == 3

    manifest2 = run_phase_2()
    assert manifest2 is not None
    assert "crewai" in manifest2.framework_configs

    manifest3 = run_phase_3()
    assert manifest3 is not None
    assert "semantic_kernel" in manifest3.framework_configs
