import os
import sys
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from graphin.config import AppConfig
from graphin.manifest.loader import load_manifest_from_yaml
from graphin.adapters import GraphInYAMLAdapter
from graphin.skillset import SkillsetManager

app = typer.Typer(
    name="graphin",
    help="Grafin CLI Engine: Coordinator of Coordinators supporting LangGraph, CrewAI, Semantic Kernel, and AGY Schedule Agents",
    add_completion=False,
)
console = Console()


@app.command("process")
def process_command(
    manifest_path: str = typer.Option("graphin.yaml", "--manifest", "-m", help="Path to GraphInYAML manifest file"),
    source_dir: str = typer.Option("examples/stem_markdown_processor/data/source", "--source-dir", "-s", help="Source directory containing input files"),
    output_dir: str = typer.Option("examples/stem_markdown_processor/data/results", "--output-dir", "-o", help="Output directory for processed artifacts"),
    confidence_threshold: float = typer.Option(0.75, "--confidence-threshold", "-t", help="Confidence threshold for automatic classification"),
    provider: str = typer.Option("gemini", "--provider", "-p", help="LLM provider ('gemini' or 'ollama')"),
):
    """Execute Grafin multi-framework workflow engine on specified GraphInYAML manifest."""
    console.print(Panel("[bold green]🚀 Launching Grafin Execution Engine (GraphInYAML)...[/bold green]"))

    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        console.print(f"[bold red]Error:[/bold red] Manifest file '{manifest_path}' not found.")
        raise typer.Exit(code=1)

    manifest = load_manifest_from_yaml(str(manifest_file))
    console.print(f"📜 Loaded GraphInYAML Manifest: [bold cyan]'{manifest.metadata.get('name')}'[/bold cyan] (v{manifest.version})")
    console.print(
        f"📋 Config: Source='{source_dir}', Output='{output_dir}', Threshold={confidence_threshold}, Provider='{provider}'"
    )

    adapter = GraphInYAMLAdapter()
    compiled_graph = adapter.build_executable(manifest)

    cfg = AppConfig(
        source_dir=source_dir,
        output_dir=output_dir,
        confidence_threshold=confidence_threshold,
        provider=provider,
    )

    initial_state = {
        "config": cfg.model_dump(),
        "classified_chunks": [],
        "pending_reviews": [],
        "saved_results": [],
    }

    thread_config = {"configurable": {"thread_id": manifest.metadata.get("name", "grafin_run")}}

    try:
        res_state = compiled_graph.invoke(initial_state, config=thread_config)
    except Exception as e:
        console.print(f"[bold red]Execution error:[/bold red] {e}")
        raise typer.Exit(code=1)

    saved_files = res_state.get("saved_results", [])
    chunks_count = len(res_state.get("classified_chunks", []))

    console.print("\n" + "=" * 70)
    console.print("[bold green]🎉 GRAFIN EXECUTION COMPLETED SUCCESSFULLY![/bold green]")
    console.print(f"📄 Saved {len(saved_files)} output artifacts to '{output_dir}'.")
    if "status_message" in res_state:
        console.print(f"ℹ️ {res_state['status_message']}")
    console.print("=" * 70 + "\n")


@app.command("connections")
def connections_command(
    manifest_path: str = typer.Option("graphin.yaml", "--manifest", "-m", help="Path to GraphInYAML manifest file"),
):
    """List and inspect shared connection access points in the manifest."""
    manifest_file = Path(manifest_path)
    if not manifest_file.exists():
        console.print(f"[bold red]Error:[/bold red] Manifest file '{manifest_path}' not found.")
        raise typer.Exit(code=1)

    manifest = load_manifest_from_yaml(str(manifest_file))
    table = Table(title=f"Shared Connections in '{manifest.metadata.get('name')}'")
    table.add_column("Connection ID", style="bold cyan")
    table.add_column("Type", style="bold magenta")
    table.add_column("Endpoint", style="bold yellow")
    table.add_column("Credentials Env", style="green")

    for c in manifest.connections:
        table.add_row(c.id, c.type, c.endpoint, c.credentials_env or "None")

    console.print(table)


@app.command("skillset")
def skillset_command(
    manifest_path: str = typer.Option("graphin.yaml", "--manifest", "-m", help="Path to GraphInYAML manifest file"),
):
    """Display registered Graph Skillsets protocol capabilities."""
    manager = SkillsetManager()
    skillset = manager.get_skillset()

    console.print(Panel("[bold green]🛠️ Grafin Graph Skillsets Protocol[/bold green]"))
    console.print(f"Available Skillsets: [bold cyan]{manager.list_skillsets()}[/bold cyan]")

    manifest_file = Path(manifest_path)
    if manifest_file.exists():
        manifest = load_manifest_from_yaml(str(manifest_file))
        if skillset:
            topology = skillset.walk_topology(manifest)
            console.print(f"\n🔍 Graph Skillset Walk Result for [bold cyan]'{manifest.metadata.get('name')}'[/bold cyan]:")
            console.print(f"   • Nodes: {topology['node_count']} | Edges: {topology['edge_count']} | Connections: {topology['connection_count']}")


if __name__ == "__main__":
    app()
