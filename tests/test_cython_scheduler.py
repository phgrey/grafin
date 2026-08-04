import pytest
from graphin.manifest.schema import ScheduleDefinition
from graphin.agents.scheduler import CrontabScheduler, PurePythonCrontabScheduler, CYTHON_AVAILABLE


def test_pure_python_scheduler_registration_and_trigger():
    scheduler = PurePythonCrontabScheduler()
    sched = ScheduleDefinition(cron="0 0 * * *", one_time=True, enabled=True)

    task_id = scheduler.register_task(
        node_id="python_node",
        schedule=sched,
        thread_id="t1",
        initial_state_update={"foo": "bar"},
    )
    assert task_id.startswith("task_")

    exec_res = scheduler.execute_trigger(task_id, current_state={"base": 1})
    assert exec_res["status"] == "success"
    assert exec_res["engine"] == "python"
    assert exec_res["updated_state"]["foo"] == "bar"


def test_cython_scheduler_availability_or_fallback():
    scheduler = CrontabScheduler()
    sched = ScheduleDefinition(cron="*/10 * * * *", one_time=False, enabled=True)

    task_id = scheduler.register_task(
        node_id="cy_node",
        schedule=sched,
        thread_id="t2",
    )
    assert task_id is not None

    exec_res = scheduler.execute_trigger(task_id)
    assert exec_res["status"] == "success"
    assert exec_res["engine"] in ("cython", "python")
