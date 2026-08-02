import sys
from pathlib import Path
from typing import Optional, Dict, Any
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from langgraph.checkpoint.memory import MemorySaver
try:
    from langgraph.types import Command
except ImportError:
    Command = None

from mac_graph.config import load_config, AppConfig
from mac_graph.manifest.loader import load_manifest_from_yaml
from mac_graph.adapters.langgraph_adapter import LangGraphAdapter
from mac_graph.hitl.dispatcher import HITLDispatcher
from mac_graph.utils.stem_taxonomy import STEM_TAXONOMY

app = typer.Typer(
    name="mac-graph",
    help="macOS Desktop Helper - Manifest-Driven STEM Document Classifier & LangGraph Workflow Runner",
)
console = Console()


def prompt_user_for_hitl_override(review_item: Dict[str, Any]) -> Dict[str, Any]:
    """Interactive CLI terminal prompt when classification confidence falls below threshold."""
    console.print("\n" + "=" * 70, style="bold red")
    console.print("⚠️  HUMAN-IN-THE-LOOP (HITL) INTERRUPT: DOUBT DETECTED", style="bold yellow")
    console.print("=" * 70, style="bold red")

    title = review_item.get("section_title", "Untitled Section")
    src = review_item.get("source_file", "Unknown")
    suggested_domain = review_item.get("suggested_primary_domain", review_item.get("primary_domain", "Unknown"))
    suggested_disc = review_item.get("suggested_discipline", review_item.get("discipline", "Unknown"))
    confidence = review_item.get("confidence_score", 0.0)
    reasoning = review_item.get("reasoning", "")
    snippet = review_item.get("content_snippet", review_item.get("content", ""))[:300]

    panel_content = (
        f"[bold cyan]Source Document:[/bold cyan] {src}\n"
        f"[bold cyan]Section Title:[/bold cyan] {title}\n"
        f"[bold yellow]Confidence Score:[/bold yellow] {confidence:.2f} (Below threshold!)\n"
        f"[bold green]LLM Suggested Domain:[/bold green] {suggested_domain}\n"
        f"[bold green]LLM Suggested Discipline:[/bold green] {suggested_disc}\n"
        f"[bold white]LLM Reasoning:[/bold white] {reasoning}\n\n"
        f"[bold dim]Content Snippet:[/bold dim]\n\"{snippet}...\""
    )
    console.print(Panel(panel_content, title="Low Confidence Classification Review", border_style="yellow"))

    console.print("[bold]Options:[/bold]")
    console.print(f"  [1] Confirm suggested tag: [bold green]'{suggested_disc}'[/bold green]")
    console.print("  [2] Pick from STEM Taxonomy list")
    console.print("  [3] Enter custom discipline name")

    choice = Prompt.ask("Select an option", choices=["1", "2", "3"], default="1")

    if choice == "1":
        return {
            "primary_domain": suggested_domain,
            "discipline": suggested_disc,
            "reasoning": f"User confirmed suggested tag '{suggested_disc}'.",
        }
    elif choice == "2":
        table = Table(title="STEM Taxonomy Domains & Subfields")
        table.add_column("Domain", style="cyan", no_wrap=True)
        table.add_column("Subfields", style="magenta")

        for dom, fields in STEM_TAXONOMY.items():
            table.add_row(dom, ", ".join(fields))

        console.print(table)

        selected_disc = Prompt.ask("Enter discipline name from taxonomy", default=suggested_disc)

        chosen_domain = suggested_domain
        for dom, fields in STEM_TAXONOMY.items():
            if any(selected_disc.lower() in f.lower() for f in fields):
                chosen_domain = dom
                break

        return {
            "primary_domain": chosen_domain,
            "discipline": selected_disc,
            "reasoning": f"User reclassified section to '{selected_disc}' under domain '{chosen_domain}'.",
        }
    else:
        custom_disc = Prompt.ask("Enter custom discipline name")
        custom_domain = Prompt.ask("Enter primary domain (Science, Technology, Engineering, Mathematics)", default="Technology")
        return {
            "primary_domain": custom_domain,
            "discipline": custom_disc,
            "reasoning": f"User specified custom tag '{custom_disc}'.",
        }


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    manifest: Optional[str] = typer.Option(None, "--manifest", "-m", help="Path to graph manifest YAML file"),
    source_dir: Optional[str] = typer.Option(None, "--source-dir", "-s", help="Path to source folder containing markdown files"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Path to directory where tagged results are saved"),
    confidence_threshold: Optional[float] = typer.Option(None, "--confidence-threshold", "-t", help="Confidence threshold score (0.0 to 1.0)"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM Provider: 'gemini' or 'ollama'"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to custom config.yaml file"),
):
    """Run the manifest-driven mac-graph execution pipeline on Markdown documents."""
    if ctx.invoked_subcommand is not None:
        return

    run_pipeline(
        manifest_path=manifest,
        source_dir=source_dir,
        output_dir=output_dir,
        confidence_threshold=confidence_threshold,
        provider=provider,
        config_file=config_file,
    )


@app.command(name="process")
def process_cmd(
    manifest: Optional[str] = typer.Option(None, "--manifest", "-m", help="Path to graph manifest YAML file"),
    source_dir: Optional[str] = typer.Option(None, "--source-dir", "-s", help="Path to source folder containing markdown files"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Path to directory where tagged results are saved"),
    confidence_threshold: Optional[float] = typer.Option(None, "--confidence-threshold", "-t", help="Confidence threshold score (0.0 to 1.0)"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="LLM Provider: 'gemini' or 'ollama'"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to custom config.yaml file"),
):
    """Subcommand: Run the manifest-driven mac-graph execution pipeline on Markdown documents."""
    run_pipeline(
        manifest_path=manifest,
        source_dir=source_dir,
        output_dir=output_dir,
        confidence_threshold=confidence_threshold,
        provider=provider,
        config_file=config_file,
    )


def run_pipeline(
    manifest_path: Optional[str] = None,
    source_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    confidence_threshold: Optional[float] = None,
    provider: Optional[str] = None,
    config_file: Optional[str] = None,
):
    console.print("[bold blue]🚀 Launching Manifest-Driven mac-graph Execution Engine...[/bold blue]")

    # 1. Load Manifest
    target_manifest_path = manifest_path or "manifest.yaml"
    if not Path(target_manifest_path).exists():
        console.print(f"[bold red]Error: Manifest file '{target_manifest_path}' not found![/bold red]")
        sys.exit(1)

    graph_manifest = load_manifest_from_yaml(target_manifest_path)
    console.print(f"📜 [dim]Loaded Graph Manifest: '{graph_manifest.metadata.get('name')}' (v{graph_manifest.version})[/dim]")

    # 2. Load Config & Apply Overrides
    cfg = load_config(config_file)
    if source_dir:
        cfg.source_dir = source_dir
    if output_dir:
        cfg.output_dir = output_dir
    if confidence_threshold is not None:
        cfg.confidence_threshold = confidence_threshold
    if provider:
        cfg.provider = provider

    console.print(
        f"📋 [dim]Config: Source='{cfg.source_dir}', Output='{cfg.output_dir}', "
        f"Threshold={cfg.confidence_threshold}, Provider='{cfg.provider}'[/dim]"
    )

    # 3. Build Executable via LangGraphAdapter
    adapter = LangGraphAdapter()
    compiled_graph = adapter.build_executable(graph_manifest)

    initial_state = {
        "config": cfg.model_dump(),
        "classified_chunks": [],
        "pending_reviews": [],
        "saved_results": [],
    }

    thread_config = {"configurable": {"thread_id": "mac-graph-manifest-run-1"}}
    hitl_dispatcher = HITLDispatcher()

    # Execute graph
    result_state = compiled_graph.invoke(initial_state, config=thread_config)

    while True:
        pending = result_state.get("pending_reviews", [])
        snapshot = compiled_graph.get_state(thread_config)

        interrupts = snapshot.tasks[0].interrupts if snapshot.tasks else ()

        if interrupts:
            hitl_item = interrupts[0].value
            hitl_dispatcher.dispatch_interrupt(hitl_item)
            user_override = prompt_user_for_hitl_override(hitl_item)

            if Command is not None:
                result_state = compiled_graph.invoke(Command(resume=user_override), config=thread_config)
            else:
                update_state = dict(result_state)
                update_state["user_override"] = user_override
                result_state = compiled_graph.invoke(update_state, config=thread_config)

        elif pending:
            hitl_item = pending[0]
            hitl_dispatcher.dispatch_interrupt(hitl_item)
            user_override = prompt_user_for_hitl_override(hitl_item)
            update_state = dict(result_state)
            update_state["user_override"] = user_override
            result_state = compiled_graph.invoke(update_state, config=thread_config)

        else:
            break

    saved_files = result_state.get("saved_results", [])
    status_msg = result_state.get("status_message", "Completed successfully.")

    console.print("\n" + "=" * 70, style="bold green")
    console.print("🎉 [bold green]MANIFEST-DRIVEN GRAPH EXECUTION COMPLETED SUCCESSFULLY![/bold green]")
    console.print(f"📄 Saved {len(saved_files)} output artifacts to '[bold cyan]{cfg.output_dir}[/bold cyan]'.")
    console.print(f"ℹ️ {status_msg}")
    console.print("=" * 70 + "\n", style="bold green")


if __name__ == "__main__":
    app()
