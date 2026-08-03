import time
import uuid
from typing import Dict, Any, List, Optional
from graphin.manifest.schema import GraphManifest, NodeDefinition, ScheduleDefinition


class CrontabScheduler:
    """Crontab Scheduler for GraphIn: Manages one-time & recurring scheduled node execution tasks and state updates."""

    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    def register_task(
        self,
        node_id: str,
        schedule: ScheduleDefinition,
        thread_id: str = "default_thread",
        initial_state_update: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Register a node schedule into the crontab queue."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        task_entry = {
            "task_id": task_id,
            "node_id": node_id,
            "cron": schedule.cron,
            "interval_seconds": schedule.interval_seconds,
            "one_time": schedule.one_time,
            "enabled": schedule.enabled,
            "created_at": time.time(),
            "last_executed_at": None,
            "status": "scheduled",
            "thread_id": thread_id,
            "state_update": initial_state_update or {},
        }
        self._tasks[task_id] = task_entry

        # Initialize checkpoint state for thread if missing
        if thread_id not in self._checkpoints:
            self._checkpoints[thread_id] = {"thread_id": thread_id, "scheduled_tasks": []}

        self._checkpoints[thread_id]["scheduled_tasks"].append(task_id)
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve scheduled task details."""
        return self._tasks.get(task_id)

    def list_tasks(self, thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all active crontab tasks, optionally filtered by thread_id."""
        if thread_id:
            return [t for t in self._tasks.values() if t["thread_id"] == thread_id]
        return list(self._tasks.values())

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled crontab task."""
        if task_id in self._tasks:
            self._tasks[task_id]["enabled"] = False
            self._tasks[task_id]["status"] = "cancelled"
            return True
        return False

    def execute_trigger(self, task_id: str, current_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a scheduled trigger, performing state update & checkpointing."""
        task = self._tasks.get(task_id)
        if not task or not task["enabled"]:
            return {"status": "error", "message": f"Task '{task_id}' not found or disabled."}

        # Perform graph state update
        state = dict(current_state or {})
        state.update(task.get("state_update", {}))
        state["last_scheduled_execution"] = {
            "task_id": task_id,
            "node_id": task["node_id"],
            "timestamp": time.time(),
        }

        task["last_executed_at"] = time.time()
        task["status"] = "executed"

        # If one_time task, disable after execution
        if task["one_time"]:
            task["enabled"] = False
            task["status"] = "completed"

        # Update checkpoint state
        thread_id = task["thread_id"]
        if thread_id in self._checkpoints:
            self._checkpoints[thread_id]["last_state"] = state
            self._checkpoints[thread_id]["last_execution_time"] = time.time()

        return {
            "status": "success",
            "task_id": task_id,
            "node_id": task["node_id"],
            "updated_state": state,
        }

    def get_checkpoint_state(self, thread_id: str) -> Dict[str, Any]:
        """Retrieve checkpoint state data for a thread."""
        return self._checkpoints.get(thread_id, {})
