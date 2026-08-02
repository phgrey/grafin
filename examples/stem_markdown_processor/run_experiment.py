import os
import sys
from pathlib import Path

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from rich.console import Console
from rich.panel import Panel

from examples.stem_markdown_processor.phase1_langgraph_export_and_run import run_phase_1
from examples.stem_markdown_processor.phase2_crewai_inject_and_run import run_phase_2
from examples.stem_markdown_processor.phase3_semantic_kernel_inspect import run_phase_3

console = Console()


def main():
    console.print("\n" + "=" * 80, style="bold green")
    console.print("🧪 SINGLE ORCHESTRATOR EXPERIMENT - MASTER RUNNER", style="bold green")
    console.print("=" * 80 + "\n", style="bold green")

    # Phase 1: LangGraph Export & Baseline Run
    manifest_p1 = run_phase_1()

    # Phase 2: CrewAI Model & Role Injection
    manifest_p2 = run_phase_2()

    # Phase 3: Semantic Kernel Inspection & Filter Execution
    manifest_p3 = run_phase_3()

    summary_text = (
        "[bold green]Single Orchestrator Experiment Successfully Completed![/bold green]\n\n"
        "1. [bold cyan]Phase 1 (LangGraph)[/bold cyan]: Exported baseline workflow & models to `stem_markdown_processor.graphin.yaml`.\n"
        "2. [bold magenta]Phase 2 (CrewAI)[/bold magenta]: Injected CrewAI tasks, roles, model configs & verified ACL hooks.\n"
        "3. [bold yellow]Phase 3 (Semantic Kernel)[/bold yellow]: Injected SK AI services, plugins & verified execution filters.\n\n"
        "📄 Final multi-framework manifest saved at: `examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml`"
    )

    console.print(Panel(summary_text, title="Experiment Execution Summary", border_style="green"))


if __name__ == "__main__":
    main()
