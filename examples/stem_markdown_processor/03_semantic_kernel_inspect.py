import os
import sys
import json
from pathlib import Path

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from rich.console import Console
from graphin.manifest.loader import load_manifest_from_yaml, save_manifest_to_yaml
from graphin.adapters.semantic_kernel_adapter import SemanticKernelAdapter

console = Console()


def run_phase_3():
    console.print("\n" + "=" * 75, style="bold yellow")
    console.print("🧠 PHASE 3: SEMANTIC KERNEL INSPECTION & FILTER EXECUTION", style="bold yellow")
    console.print("=" * 75, style="bold yellow")

    manifest_file = "examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml"
    manifest = load_manifest_from_yaml(manifest_file)
    console.print(f"📖 Loaded GraphInYAML manifest '{manifest.metadata.get('name')}'.")

    # 1. Inject Semantic Kernel Framework Configuration
    adapter = SemanticKernelAdapter(filter_allowed_actions=["add_node", "inspect_graph"])

    sk_cfg = {
        "service_id": "default_sk_service",
        "plugins": ["GraphManipulationPlugin"],
    }
    manifest = adapter.inject_config(manifest, sk_cfg)

    # 2. Build Executable Semantic Kernel Service Registry
    sk_executable = adapter.build_executable(manifest)
    console.print(f"✅ Registered {len(sk_executable.get('plugins', {}))} Semantic Kernel Plugins.")
    console.print(f"📡 AI ChatCompletion Services bound: {list(sk_executable.get('ai_services', {}).keys())}")

    # 3. Test GraphManipulationPlugin & Function Execution Filters
    plugin = adapter.get_tool_wrapper(manifest)

    # Inspect graph topology via SK plugin
    inspection_res = plugin.manipulate_graph(action="inspect_graph")
    parsed_manifest = json.loads(inspection_res)
    console.print(f"🔍 SK Graph Inspection: Manifest contains {len(parsed_manifest.get('nodes', []))} nodes and {len(parsed_manifest.get('models', []))} model connection definitions.")

    # Attempt forbidden action -> Should be blocked by SK Execution Filter
    res_blocked = plugin.manipulate_graph(action="remove_node", node_id="load_documents")
    console.print(f"🔒 SK Filter Test (Blocked Removal): {res_blocked}")
    assert "ACL_DENIED" in res_blocked

    # Save final multi-framework manifest
    save_manifest_to_yaml(manifest, manifest_file)
    console.print(f"📄 Saved final Multi-Framework GraphInYAML manifest to '[bold cyan]{manifest_file}[/bold cyan]'.")
    console.print("🎉 [bold green]Phase 3 Complete![/bold green]\n")
    return manifest


if __name__ == "__main__":
    run_phase_3()
