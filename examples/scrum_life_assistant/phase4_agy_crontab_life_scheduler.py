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
    console.print("⏰ EXPERIMENT #2 - PHASE 4: AGY SCHEDULE AGENTS & CRONTAB LIFE SCHEDULER", style="bold blue")
    console.print("=" * 75, style="bold blue")

    manifest_file = "examples/scrum_life_assistant/scrum_life_assistant.graphin.yaml"
    manifest = load_manifest_from_yaml(manifest_file)
    console.print(f"📖 Loaded GraphInYAML manifest '{manifest.metadata.get('name')}'.")

    scheduler = CrontabScheduler()
    reader_agent = GraphinReaderAgent(name="SCRUM_GraphinReader")
    writer_agent = GraphinWriterAgent(name="SCRUM_GraphinWriter")

    # 1. Reader Agent walks graph topology
    graph_topology = reader_agent.walk_graph(manifest)
    console.print(f"🔍 [bold cyan]{reader_agent.name}[/bold cyan] walked graph: Found {graph_topology['node_count']} nodes, {graph_topology['edge_count']} edges.")

    # 2. Writer Agent schedules Doctor Appointment task into crontab
    sched_doc = writer_agent.schedule_node_task(
        manifest=manifest,
        scheduler=scheduler,
        node_id="life_scheduler",
        cron="0 9 * * *",
        one_time=True,
        thread_id="doctor_appointment_thread",
        state_update={"appointment": "Annual Health Checkup", "reminder_sent": True},
    )
    console.print(f"✍️ [bold magenta]{writer_agent.name}[/bold magenta] scheduled Doctor Appointment: Task ID = '{sched_doc['task_id']}'.")

    # 3. Writer Agent schedules Recurring STEM Sub-Graph Processor Task (Example #1)
    sched_stem = writer_agent.schedule_node_task(
        manifest=manifest,
        scheduler=scheduler,
        node_id="stem_subgraph",
        cron="0 1 * * *",
        interval_seconds=86400,
        one_time=False,
        enabled=True,
        thread_id="recurring_stem_batch_thread",
        state_update={"trigger_source": "recurring_crontab", "subgraph": "stem_markdown_processor"},
    )
    console.print(f"✍️ [bold magenta]{writer_agent.name}[/bold magenta] scheduled Recurring STEM Sub-Graph Task (Example #1): Task ID = '{sched_stem['task_id']}'.")

    save_manifest_to_yaml(manifest, manifest_file)

    # 4. Reader Agent inspects crontab queue
    active_schedules = reader_agent.inspect_schedule(scheduler)
    console.print(f"📋 [bold cyan]{reader_agent.name}[/bold cyan] inspected active crontab queue: Found {len(active_schedules)} registered tasks.")
    for task in active_schedules:
        console.print(f"   • Task '{task['task_id']}': Node='{task['node_id']}', Cron='{task['cron']}', OneTime={task['one_time']}, Status='{task['status']}'")

    # 5. Trigger Crontab Execution & Update Checkpoint State
    exec_res = scheduler.execute_trigger(task_id=sched_stem["task_id"])
    console.print(f"⚡ Executed Crontab Task '{sched_stem['task_id']}': Status = '{exec_res['status']}'.")
    console.print(f"💾 Graph Checkpoint Updated with Recurring Sub-Graph Run: {exec_res['updated_state']['subgraph']}")

    console.print("🎉 [bold green]Phase 4 Complete![/bold green]\n")
    return manifest


if __name__ == "__main__":
    run_phase_4()
