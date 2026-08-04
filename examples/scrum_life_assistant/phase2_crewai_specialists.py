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
    console.print("🤖 EXPERIMENT #2 - PHASE 2: CREWAI SPECIALIST TEAM & ACL HOOKS", style="bold magenta")
    console.print("=" * 75, style="bold magenta")

    manifest_file = "examples/scrum_life_assistant/scrum_life_assistant.graphin.yaml"
    manifest = load_manifest_from_yaml(manifest_file)
    console.print(f"📖 Loaded GraphInYAML manifest '{manifest.metadata.get('name')}'.")

    adapter = CrewAIAdapter(acl_policy="admin_only_node_deletion")

    crewai_cfg = {
        "verbose": True,
        "process": "hierarchical",
        "manager_llm": "gemini-1.5-flash",
        "acl_policy": "admin_only_node_deletion",
        "specialists": ["ResumeAuditor", "FinancialAuditor", "GitHubPRReviewer"],
    }
    manifest = adapter.inject_config(manifest, crewai_cfg)

    executable_crew = adapter.build_executable(manifest)
    console.print(f"✅ Generated CrewAI Workflow with {len(executable_crew.get('tasks', []))} specialist tasks.")

    tool = adapter.get_tool_wrapper(manifest)

    res_user = tool._run(action="remove_node", node_id="cv_refiner", agent_role="junior_dev")
    console.print(f"🔒 ACL Test (Non-Admin Deletion Blocked): {res_user}")
    assert "ACL DENIED" in res_user

    res_admin_add = tool._run(
        action="add_node",
        node_id="pr_code_review",
        node_type="agent",
        code_ref="examples.scrum_life_assistant.nodes:audit",
        agent_role="admin",
    )
    console.print(f"🔓 ACL Test (Admin Node Addition Allowed): {res_admin_add}")
    assert "SUCCESS" in res_admin_add

    save_manifest_to_yaml(manifest, manifest_file)
    console.print(f"📄 Saved updated CrewAI-injected manifest to '[bold cyan]{manifest_file}[/bold cyan]'.")
    console.print("🎉 [bold green]Phase 2 Complete![/bold green]\n")
    return manifest


if __name__ == "__main__":
    run_phase_2()
