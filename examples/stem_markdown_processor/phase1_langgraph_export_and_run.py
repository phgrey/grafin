import os
import sys
from pathlib import Path

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from rich.console import Console

try:
    from langgraph.types import Command
except ImportError:
    Command = None

from graphin.config import AppConfig
from graphin.state import GraphState
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition, ModelDefinition
from graphin.manifest.loader import save_manifest_to_yaml, load_manifest_from_yaml
from graphin.adapters.langgraph_adapter import LangGraphAdapter
from examples.stem_markdown_processor.nodes.document_loader import load_documents_node
from examples.stem_markdown_processor.nodes.semantic_chunker import semantic_chunker_node
from examples.stem_markdown_processor.nodes.stem_classifier import stem_classifier_node, check_confidence_routing
from examples.stem_markdown_processor.nodes.result_saver import save_results_node
from graphin.nodes.human_review import human_review_node

console = Console()


def run_phase_1(interactive: bool = False):
    console.print("\n" + "=" * 75, style="bold cyan")
    console.print("🚀 PHASE 1: LANGGRAPH NATIVE BASELINE & MANIFEST EXPORT", style="bold cyan")
    console.print("=" * 75, style="bold cyan")

    builder = StateGraph(GraphState)
    builder.add_node("load_documents", load_documents_node)
    builder.add_node("semantic_chunker", semantic_chunker_node)
    builder.add_node("stem_classifier", stem_classifier_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("save_results", save_results_node)

    builder.add_edge(START, "load_documents")
    builder.add_edge("load_documents", "semantic_chunker")
    builder.add_edge("semantic_chunker", "stem_classifier")
    builder.add_conditional_edges("stem_classifier", check_confidence_routing, {"human_review": "human_review", "save_results": "save_results"})
    builder.add_conditional_edges("human_review", check_confidence_routing, {"human_review": "human_review", "save_results": "save_results"})
    builder.add_edge("save_results", END)

    compiled_native = builder.compile(checkpointer=MemorySaver())
    console.print("✅ Compiled native LangGraph StateGraph.")

    manifest = GraphManifest(
        version="0.1.0",
        metadata={
            "name": "stem_markdown_processor",
            "description": "Single Orchestrator Experiment STEM Markdown Processor",
            "author": "graphin team",
        },
        models=[
            ModelDefinition(
                id="gemini_flash",
                provider="gemini",
                model_name="gemini-1.5-flash",
                protocol="https",
                endpoint="https://generativelanguage.googleapis.com",
                api_key_env="GEMINI_API_KEY",
                parameters={"temperature": 0.1},
            ),
            ModelDefinition(
                id="local_ollama",
                provider="ollama",
                model_name="llama3.1",
                protocol="http",
                endpoint="http://localhost:11434",
                api_key_env="OLLAMA_API_KEY",
                parameters={"temperature": 0.1},
            ),
            ModelDefinition(
                id="hf_mistral",
                provider="huggingface",
                model_name="mistralai/Mistral-7B-Instruct-v0.2",
                protocol="https",
                endpoint="https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                api_key_env="HUGGINGFACE_API_KEY",
                parameters={"temperature": 0.1},
            ),
        ],
        default_model_ref="gemini_flash",
        nodes=[
            NodeDefinition(id="load_documents", type="function", code_ref="examples.stem_markdown_processor.nodes.document_loader:load_documents_node", description="Loads markdown files"),
            NodeDefinition(id="semantic_chunker", type="function", code_ref="examples.stem_markdown_processor.nodes.semantic_chunker:semantic_chunker_node", description="Splits markdown into section chunks"),
            NodeDefinition(id="stem_classifier", type="function", code_ref="examples.stem_markdown_processor.nodes.stem_classifier:stem_classifier_node", description="Classifies chunks into STEM taxonomy"),
            NodeDefinition(id="human_review", type="interrupt", code_ref="graphin.nodes.human_review:human_review_node", description="HITL review node for low confidence classifications"),
            NodeDefinition(id="save_results", type="function", code_ref="examples.stem_markdown_processor.nodes.result_saver:save_results_node", description="Exports tagged results"),
        ],
        edges=[
            EdgeDefinition(source="__start__", target="load_documents"),
            EdgeDefinition(source="load_documents", target="semantic_chunker"),
            EdgeDefinition(source="semantic_chunker", target="stem_classifier"),
            EdgeDefinition(source="stem_classifier", condition_ref="examples.stem_markdown_processor.nodes.stem_classifier:check_confidence_routing", branches={"human_review": "human_review", "save_results": "save_results"}),
            EdgeDefinition(source="human_review", condition_ref="examples.stem_markdown_processor.nodes.stem_classifier:check_confidence_routing", branches={"human_review": "human_review", "save_results": "save_results"}),
            EdgeDefinition(source="save_results", target="__end__"),
        ],
        framework_configs={
            "langgraph": {"checkpointer": "MemorySaver"},
        },
    )

    manifest_file = "examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml"
    save_manifest_to_yaml(manifest, manifest_file)
    console.print(f"📄 Exported GraphInYAML Manifest to '[bold cyan]{manifest_file}[/bold cyan]'.")

    adapter = LangGraphAdapter()
    compiled_from_manifest = adapter.build_executable(manifest)

    # In non-interactive mode (e.g. tests), set threshold lower (0.10) so all items auto-pass without HITL pause
    threshold = 0.50 if interactive else 0.10

    cfg = AppConfig(
        source_dir="examples/stem_markdown_processor/data/source",
        output_dir="examples/stem_markdown_processor/data/results",
        confidence_threshold=threshold,
    )

    initial_state = {
        "config": cfg.model_dump(),
        "classified_chunks": [],
        "pending_reviews": [],
        "saved_results": [],
    }

    thread_config = {"configurable": {"thread_id": "phase1-run"}}
    res_state = compiled_from_manifest.invoke(initial_state, config=thread_config)

    # Handle any remaining pending reviews if paused
    while True:
        pending = res_state.get("pending_reviews", [])
        if not pending:
            break
        # Automatic non-interactive confirmation for test stability
        auto_override = {
            "primary_domain": pending[0].get("primary_domain", "Technology"),
            "discipline": pending[0].get("discipline", "Information Systems"),
            "reasoning": "Automated test review confirmation.",
        }
        if Command is not None:
            res_state = compiled_from_manifest.invoke(Command(resume=auto_override), config=thread_config)
        else:
            up = dict(res_state)
            up["user_override"] = auto_override
            res_state = compiled_from_manifest.invoke(up, config=thread_config)

    saved_files = res_state.get("saved_results", [])
    console.print(f"🎉 [bold green]Phase 1 Complete![/bold green] Processed {len(res_state.get('classified_chunks', []))} chunks across {len(saved_files)} files.\n")
    return manifest


if __name__ == "__main__":
    run_phase_1(interactive=True)
