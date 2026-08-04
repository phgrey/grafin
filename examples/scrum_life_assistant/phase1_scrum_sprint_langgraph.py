import os
import sys
from pathlib import Path

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from rich.console import Console

from graphin.config import AppConfig
from graphin.state import GraphState
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition, ModelDefinition, ConnectionDefinition, WorkspaceConfig, ScheduleDefinition
from graphin.manifest.loader import save_manifest_to_yaml
from graphin.adapters.langgraph_adapter import LangGraphAdapter
from graphin.agents.github_agent import github_agent_node
from examples.scrum_life_assistant.nodes.sprint_planner import sprint_planner_node
from examples.scrum_life_assistant.nodes.cv_refiner import cv_refiner_node
from examples.scrum_life_assistant.nodes.budget_auditor import budget_auditor_node
from examples.scrum_life_assistant.nodes.life_scheduler import life_scheduler_node
from examples.scrum_life_assistant.nodes.stem_subgraph_node import stem_processor_subgraph_node

console = Console()


def run_phase_1():
    console.print("\n" + "=" * 75, style="bold cyan")
    console.print("🚀 EXPERIMENT #2 - PHASE 1: LANGGRAPH SCRUM SPRINT & SUB-GRAPH NODE", style="bold cyan")
    console.print("=" * 75, style="bold cyan")

    # 1. Build Native LangGraph StateGraph Workflow with Embedded Sub-Graph Node
    builder = StateGraph(GraphState)
    builder.add_node("sprint_planner", sprint_planner_node)
    builder.add_node("github_flow", github_agent_node)
    builder.add_node("cv_refiner", cv_refiner_node)
    builder.add_node("budget_auditor", budget_auditor_node)
    builder.add_node("stem_subgraph", stem_processor_subgraph_node)
    builder.add_node("life_scheduler", life_scheduler_node)

    builder.add_edge(START, "sprint_planner")
    builder.add_edge("sprint_planner", "github_flow")
    builder.add_edge("github_flow", "cv_refiner")
    builder.add_edge("cv_refiner", "budget_auditor")
    builder.add_edge("budget_auditor", "stem_subgraph")
    builder.add_edge("stem_subgraph", "life_scheduler")
    builder.add_edge("life_scheduler", END)

    compiled_native = builder.compile(checkpointer=MemorySaver())
    console.print("✅ Compiled native LangGraph StateGraph with Embedded STEM Sub-Graph Node.")

    # 2. Construct GraphInYAML Manifest with Connections, Models, and Sub-Graph Schedule
    manifest = GraphManifest(
        version="0.1.0",
        metadata={
            "name": "scrum_life_assistant",
            "description": "Multi-Agent SCRUM & Life Assistant Graph with Embedded STEM Sub-Graph",
            "author": "graphin team",
        },
        models=[
            ModelDefinition(id="gemini_flash", provider="gemini", model_name="gemini-1.5-flash", api_key_env="GEMINI_API_KEY"),
            ModelDefinition(id="local_ollama", provider="ollama", model_name="llama3.1", endpoint="http://localhost:11434"),
        ],
        connections=[
            ConnectionDefinition(id="sprint_db", type="mysql", endpoint="localhost:3306", credentials_env="DB_PASS"),
            ConnectionDefinition(id="dev_pipe", type="unix_socket", endpoint="/tmp/grafin_scrum.sock"),
        ],
        workspace=WorkspaceConfig(
            devcontainers=[".devcontainer/devcontainer.json"],
            docker_containers=["scrum_logger"],
            local_cloud_models={"primary": "gemini-1.5-flash"},
        ),
        nodes=[
            NodeDefinition(id="sprint_planner", type="function", code_ref="examples.scrum_life_assistant.nodes.sprint_planner:sprint_planner_node", description="SCRUM backlog planner"),
            NodeDefinition(id="github_flow", type="agent", code_ref="graphin.agents.github_agent:github_agent_node", description="GitHub Agent managing feature branches & PRs"),
            NodeDefinition(id="cv_refiner", type="function", code_ref="examples.scrum_life_assistant.nodes.cv_refiner:cv_refiner_node", description="Refines developer resume"),
            NodeDefinition(id="budget_auditor", type="function", code_ref="examples.scrum_life_assistant.nodes.budget_auditor:budget_auditor_node", description="Audits expense budgets"),
            NodeDefinition(
                id="stem_subgraph",
                type="subgraph",
                code_ref="examples.scrum_life_assistant.nodes.stem_subgraph_node:stem_processor_subgraph_node",
                description="Recurring STEM Markdown Processor sub-workflow (Example #1)",
                schedule=ScheduleDefinition(cron="0 1 * * *", one_time=False, enabled=True),
            ),
            NodeDefinition(id="life_scheduler", type="function", code_ref="examples.scrum_life_assistant.nodes.life_scheduler:life_scheduler_node", description="Schedules doctor appointments & side tasks"),
        ],
        edges=[
            EdgeDefinition(source="__start__", target="sprint_planner"),
            EdgeDefinition(source="sprint_planner", target="github_flow"),
            EdgeDefinition(source="github_flow", target="cv_refiner"),
            EdgeDefinition(source="cv_refiner", target="budget_auditor"),
            EdgeDefinition(source="budget_auditor", target="stem_subgraph"),
            EdgeDefinition(source="stem_subgraph", target="life_scheduler"),
            EdgeDefinition(source="life_scheduler", target="__end__"),
        ],
        framework_configs={"langgraph": {"checkpointer": "MemorySaver"}},
    )

    manifest_file = "examples/scrum_life_assistant/scrum_life_assistant.graphin.yaml"
    save_manifest_to_yaml(manifest, manifest_file)
    console.print(f"📄 Exported GraphInYAML Manifest to '[bold cyan]{manifest_file}[/bold cyan]'.")

    # 3. Execute via LangGraphAdapter
    adapter = LangGraphAdapter()
    compiled_from_manifest = adapter.build_executable(manifest)

    initial_state = {"config": {"confidence_threshold": 0.50}, "classified_chunks": [], "pending_reviews": [], "saved_results": []}
    thread_config = {"configurable": {"thread_id": "scrum-phase1-run"}}
    res_state = compiled_from_manifest.invoke(initial_state, config=thread_config)

    sg_info = res_state.get("stem_subgraph_info", {})
    console.print(f"🎉 [bold green]Phase 1 Complete![/bold green] Embedded Sub-Graph Executed: '[bold cyan]{sg_info.get('manifest_name')}[/bold cyan]' ({sg_info.get('node_count')} nodes).\n")
    return manifest


if __name__ == "__main__":
    run_phase_1()
