import os
import sys
from pathlib import Path

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from rich.console import Console
from graphin.manifest.loader import load_manifest_from_yaml, save_manifest_to_yaml
from graphin.adapters.crewai_adapter import CrewAIAdapter
from graphin.manifest.schema import NodeDefinition

console = Console()


def run_phase_2():
    console.print("\n" + "=" * 75, style="bold magenta")
    console.print("🤖 PHASE 2: CREWAI INJECTION & ACL TOOL EXECUTION", style="bold magenta")
    console.print("=" * 75, style="bold magenta")

    manifest_file = "examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml"
    manifest = load_manifest_from_yaml(manifest_file)
    console.print(f"📖 Loaded GraphInYAML manifest '{manifest.metadata.get('name')}'.")

    adapter = CrewAIAdapter(acl_policy="admin_only_node_deletion")

    crewai_cfg = {
        "verbose": True,
        "process": "hierarchical",
        "manager_llm": "gemini-1.5-flash",
        "acl_policy": "admin_only_node_deletion",
    }
    manifest = adapter.inject_config(manifest, crewai_cfg)

    executable_crew = adapter.build_executable(manifest)
    console.print(f"✅ Generated CrewAI Workflow with {len(executable_crew.get('tasks', []))} tasks.")
    console.print(f"📋 Model Bindings adopted by CrewAI Adapter: {list(executable_crew.get('crewai_llm_configs', {}).keys())}")

    tool = adapter.get_tool_wrapper(manifest)

    res_user = tool._run(action="remove_node", node_id="human_review", agent_role="analyst_agent")
    console.print(f"🔒 ACL Test (Non-Admin): {res_user}")
    assert "ACL DENIED" in res_user

    res_admin_add = tool._run(
        action="add_node",
        node_id="quality_audit",
        node_type="agent",
        code_ref="examples.stem_markdown_processor.nodes:audit",
        agent_role="admin",
    )
    console.print(f"🔓 ACL Test (Admin Add): {res_admin_add}")
    assert "SUCCESS" in res_admin_add

    save_manifest_to_yaml(manifest, manifest_file)
    console.print(f"📄 Saved updated CrewAI-injected manifest to '[bold cyan]{manifest_file}[/bold cyan]'.")
    console.print("🎉 [bold green]Phase 2 Complete![/bold green]\n")
    return manifest


if __name__ == "__main__":
    run_phase_2()
