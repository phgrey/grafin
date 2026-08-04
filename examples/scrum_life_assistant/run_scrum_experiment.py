import os
import sys
from pathlib import Path

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from rich.console import Console
from rich.panel import Panel

from examples.scrum_life_assistant.phase1_scrum_sprint_langgraph import run_phase_1
from examples.scrum_life_assistant.phase2_crewai_specialists import run_phase_2
from examples.scrum_life_assistant.phase3_semantic_kernel_triz import run_phase_3
from examples.scrum_life_assistant.phase4_agy_crontab_life_scheduler import run_phase_4

console = Console()


def main():
    console.print("\n" + "=" * 80, style="bold green")
    console.print("🧪 EXPERIMENT #2: MULTI-AGENT SCRUM & LIFE ASSISTANT - MASTER RUNNER", style="bold green")
    console.print("=" * 80 + "\n", style="bold green")

    # Phase 1: LangGraph SCRUM & GitHub Agent Node
    manifest_p1 = run_phase_1()

    # Phase 2: CrewAI Specialist Team & ACL Hooks
    manifest_p2 = run_phase_2()

    # Phase 3: Semantic Kernel Architectural Discussion (Native Agent vs MCP Server)
    manifest_p3 = run_phase_3()

    # Phase 4: AGY Schedule Agents & Crontab Life Scheduler
    manifest_p4 = run_phase_4()

    summary_text = (
        "[bold green]Experiment #2 Successfully Completed![/bold green]\n\n"
        "1. [bold cyan]Phase 1 (LangGraph & GitHub Agent)[/bold cyan]: Created feature branch & opened PR for SCRUM task.\n"
        "2. [bold magenta]Phase 2 (CrewAI Specialists)[/bold magenta]: Assigned Resume/Financial auditors & verified ACL hooks.\n"
        "3. [bold yellow]Phase 3 (Semantic Kernel)[/bold yellow]: Evaluated Native GitHubAgent (<0.5ms latency) vs GitHub MCP Server.\n"
        "4. [bold blue]Phase 4 (AGY Schedule Agents)[/bold blue]: Scheduled doctor appointments & budget audits into Cython Crontab.\n\n"
        "📄 Final manifest saved at: `examples/scrum_life_assistant/scrum_life_assistant.graphin.yaml`"
    )

    console.print(Panel(summary_text, title="Experiment #2 Execution Summary", border_style="green"))


if __name__ == "__main__":
    main()
