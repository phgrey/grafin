import pytest
from graphin.manifest.schema import GraphManifest, NodeDefinition, ScheduleDefinition
from graphin.agents.scheduler import CrontabScheduler
from graphin.agents.reader_agent import GraphinReaderAgent
from graphin.agents.writer_agent import GraphinWriterAgent


def test_schedule_definition_schema():
    sched = ScheduleDefinition(cron="0 0 * * *", one_time=False, enabled=True)
    assert sched.cron == "0 0 * * *"
    assert sched.one_time is False
    assert sched.enabled is True

    node = NodeDefinition(
        id="scheduled_task",
        type="function",
        code_ref="module:func",
        schedule=sched,
    )
    assert node.schedule is not None
    assert node.schedule.cron == "0 0 * * *"


def test_crontab_scheduler_registration_and_execution():
    scheduler = CrontabScheduler()
    sched = ScheduleDefinition(cron="*/5 * * * *", one_time=True, enabled=True)

    task_id = scheduler.register_task(
        node_id="test_node",
        schedule=sched,
        thread_id="thread_1",
        initial_state_update={"flag": True},
    )

    assert task_id.startswith("task_")
    task = scheduler.get_task(task_id)
    assert task is not None
    assert task["node_id"] == "test_node"
    assert task["status"] == "scheduled"

    # Execute trigger
    res = scheduler.execute_trigger(task_id, current_state={"counter": 1})
    assert res["status"] == "success"
    assert res["updated_state"]["flag"] is True
    assert res["updated_state"]["counter"] == 1
    assert "last_scheduled_execution" in res["updated_state"]

    # Verify one-time task completed
    task_after = scheduler.get_task(task_id)
    assert task_after["status"] == "completed"
    assert task_after["enabled"] is False


def test_graphin_reader_and_writer_agents():
    manifest = GraphManifest(
        version="0.1.0",
        metadata={"name": "test_manifest"},
        nodes=[
            NodeDefinition(id="n1", type="function", code_ref="m:f1"),
            NodeDefinition(id="n2", type="function", code_ref="m:f2"),
        ],
    )
    scheduler = CrontabScheduler()

    reader_agent = GraphinReaderAgent(name="TestReader")
    writer_agent = GraphinWriterAgent(name="TestWriter")

    # Walk topology
    topology = reader_agent.walk_graph(manifest)
    assert topology["node_count"] == 2
    assert topology["agent_name"] == "TestReader"

    # Writer agent schedules node task
    sched_res = writer_agent.schedule_node_task(
        manifest=manifest,
        scheduler=scheduler,
        node_id="n1",
        cron="0 12 * * *",
        one_time=True,
        thread_id="test_thread",
        state_update={"scheduled_by": "TestWriter"},
    )
    assert sched_res["status"] == "success"
    assert manifest.get_node("n1").schedule is not None
    assert manifest.get_node("n1").schedule.cron == "0 12 * * *"

    # Reader agent inspects registered schedule
    tasks = reader_agent.inspect_schedule(scheduler, thread_id="test_thread")
    assert len(tasks) == 1
    assert tasks[0]["node_id"] == "n1"

    # Writer agent updates checkpoint state
    chk_res = writer_agent.update_checkpoint_state(
        scheduler, thread_id="test_thread", state_data={"checkpoint_status": "ok"}
    )
    assert chk_res["status"] == "success"

    # Reader agent verifies checkpoint
    chk_data = reader_agent.read_checkpoint_state(scheduler, thread_id="test_thread")
    assert chk_data.get("checkpoint_status") == "ok"
