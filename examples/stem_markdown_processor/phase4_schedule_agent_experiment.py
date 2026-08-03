import os
import sys
from pathlib import Path

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from rich.console import Console
from graphin.manifest.loader import load_manifest_from_yaml, save_manifest_to_yaml
from graphin.agents.scheduler import CrontabScheduler
from graphin.agents.reader_agent import GraphinReaderAgent
from graphin.agents.writer_agent import GraphinWriterAgent

console = Console()


def run_phase_4():
    console.print("\n" + "=" * 75, style="bold blue")
    console.print("⏰ PHASE 4: GOOGLE ANTIGRAVITY SDK SCHEDULE AGENTS (READER & WRITER)", style="bold blue")
    console.print("=" * 75, style="bold blue")

    manifest_file = "examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml"
    manifest = load_manifest_from_yaml(manifest_file)
    console.print(f"📖 Loaded GraphInYAML manifest '{manifest.metadata.get('name')}'.")

    scheduler = CrontabScheduler()
    reader_agent = GraphinReaderAgent(name="STEM_GraphinReader")
    writer_agent = GraphinWriterAgent(name="STEM_GraphinWriter")

    # 1. Reader Agent walks graph topology
    graph_topology = reader_agent.walk_graph(manifest)
    console.print(f"🔍 [bold cyan]{reader_agent.name}[/bold cyan] walked graph: Found {graph_topology['node_count']} nodes, {graph_topology['edge_count']} edges.")

    # 2. Writer Agent schedules a one-time classification task into crontab
    sched_res = writer_agent.schedule_node_task(
        manifest=manifest,
        scheduler=scheduler,
        node_id="stem_classifier",
        cron="0 2 * * *",
        one_time=True,
        enabled=True,
        thread_id="nightly_batch_thread",
        state_update={"trigger_source": "schedule_agent", "batch_priority": "high"},
    )
    console.print(f"✍️ [bold magenta]{writer_agent.name}[/bold magenta] scheduled node '{sched_res['node_id']}': Task ID = '{sched_res['task_id']}'.")

    # Save manifest with updated node schedule parameters
    save_manifest_to_yaml(manifest, manifest_file)
    console.print(f"📄 Saved manifest with node schedule definitions to '[bold cyan]{manifest_file}[/bold cyan]'.")

    # 3. Reader Agent inspects registered crontab schedules
    active_schedules = reader_agent.inspect_schedule(scheduler, thread_id="nightly_batch_thread")
    console.print(f"📋 [bold cyan]{reader_agent.name}[/bold cyan] inspected crontab tasks: Found {len(active_schedules)} registered tasks.")
    for task in active_schedules:
        console.print(f"   • Task '{task['task_id']}': Node='{task['node_id']}', Cron='{task['cron']}', OneTime={task['one_time']}, Status='{task['status']}'")

    # 4. Trigger Crontab Execution & Update Checkpoint State
    trigger_task_id = sched_res["task_id"]
    exec_res = scheduler.execute_trigger(task_id=trigger_task_id, current_state={"initial_files_count": 5})
    console.print(f"⚡ Executed Crontab Task '{trigger_task_id}': Status = '{exec_res['status']}'.")
    console.print(f"💾 Graph State Updated with Schedule Timestamp: {exec_res['updated_state']['last_scheduled_execution']}")

    # 5. Reader Agent verifies updated checkpoint state
    checkpoint = reader_agent.read_checkpoint_state(scheduler, thread_id="nightly_batch_thread")
    console.print(f"🔍 [bold cyan]{reader_agent.name}[/bold cyan] verified checkpoint state: Last execution time recorded.")

    console.print("🎉 [bold green]Phase 4 Complete![/bold green]\n")
    return manifest


if __name__ == "__main__":
    run_phase_4()
