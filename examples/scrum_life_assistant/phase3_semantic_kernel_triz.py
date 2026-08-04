import os
import sys
import json
from pathlib import Path

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from graphin.manifest.loader import load_manifest_from_yaml, save_manifest_to_yaml
from graphin.adapters.semantic_kernel_adapter import SemanticKernelAdapter

console = Console()


def run_phase_3():
    console.print("\n" + "=" * 75, style="bold yellow")
    console.print("🧠 EXPERIMENT #2 - PHASE 3: SEMANTIC KERNEL ARCHITECTURAL DISCUSSION", style="bold yellow")
    console.print("=" * 75, style="bold yellow")

    manifest_file = "examples/scrum_life_assistant/scrum_life_assistant.graphin.yaml"
    manifest = load_manifest_from_yaml(manifest_file)
    console.print(f"📖 Loaded GraphInYAML manifest '{manifest.metadata.get('name')}'.")

    adapter = SemanticKernelAdapter(filter_allowed_actions=["add_node", "inspect_graph"])

    sk_cfg = {
        "service_id": "default_sk_service",
        "plugins": ["GraphManipulationPlugin", "GitHubComparisonPlugin"],
    }
    manifest = adapter.inject_config(manifest, sk_cfg)

    # Architectural Discussion Report: Native GitHubAgent Callable vs. GitHub MCP Server
    console.print("\n", Panel("[bold yellow]ARCHITECTURAL EVALUATION: Native GitHubAgent vs. GitHub MCP Server[/bold yellow]"))

    table = Table(title="Semantic Kernel Evaluation Matrix")
    table.add_column("Evaluation Dimension", style="bold cyan")
    table.add_column("Native GitHubAgent Callable", style="bold green")
    table.add_column("GitHub MCP Server", style="bold magenta")

    table.add_row("Execution Latency", "< 0.5 ms (In-process C/Python call)", "~10-50 ms (IPC / Socket JSON-RPC overhead)")
    table.add_row("State Binding", "Direct binding to GraphIn state & checkpoints", "Decoupled tool context protocol")
    table.add_row("Cross-Language Portability", "Python/Cython specific", "Framework-agnostic JSON-RPC protocol")
    table.add_row("Security & ACL Isolation", "GraphIn internal ACL hooks", "Sandboxed external process boundary")
    table.add_row("Recommendation", "OPTIMAL for high-throughput GraphIn nodes", "OPTIMAL for cross-system tool sharing")

    console.print(table)

    plugin = adapter.get_tool_wrapper(manifest)
    inspection_res = plugin.manipulate_graph(action="inspect_graph")
    parsed_manifest = json.loads(inspection_res)
    console.print(f"\n🔍 SK Inspection: Manifest contains {len(parsed_manifest.get('nodes', []))} nodes and {len(parsed_manifest.get('connections', []))} connection access points.")

    save_manifest_to_yaml(manifest, manifest_file)
    console.print(f"📄 Saved updated Semantic Kernel manifest to '[bold cyan]{manifest_file}[/bold cyan]'.")
    console.print("🎉 [bold green]Phase 3 Complete![/bold green]\n")
    return manifest


if __name__ == "__main__":
    run_phase_3()
