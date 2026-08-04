# cython: language_level=3
import time
import uuid

cdef class CythonCrontabScheduler:
    """Cython-accelerated Crontab Scheduler for GraphIn performance task queuing and state operations."""
    
    cdef public dict _tasks
    cdef public dict _checkpoints

    def __init__(self):
        self._tasks = {}
        self._checkpoints = {}

    def register_task(
        self,
        str node_id,
        object schedule,
        str thread_id="default_thread",
        object initial_state_update=None,
    ) -> str:
        """Register a node schedule into the Cython crontab queue."""
        cdef str task_id = f"task_cy_{uuid.uuid4().hex[:8]}"
        cdef double now = time.time()

        task_entry = {
            "task_id": task_id,
            "node_id": node_id,
            "cron": getattr(schedule, "cron", None),
            "interval_seconds": getattr(schedule, "interval_seconds", None),
            "one_time": getattr(schedule, "one_time", False),
            "enabled": getattr(schedule, "enabled", True),
            "created_at": now,
            "last_executed_at": None,
            "status": "scheduled",
            "thread_id": thread_id,
            "state_update": initial_state_update or {},
            "engine": "cython",
        }
        self._tasks[task_id] = task_entry

        if thread_id not in self._checkpoints:
            self._checkpoints[thread_id] = {"thread_id": thread_id, "scheduled_tasks": []}

        self._checkpoints[thread_id]["scheduled_tasks"].append(task_id)
        return task_id

    def get_task(self, str task_id):
        """Retrieve scheduled task details."""
        return self._tasks.get(task_id)

    def list_tasks(self, object thread_id=None):
        """List all active crontab tasks."""
        if thread_id:
            return [t for t in self._tasks.values() if t["thread_id"] == thread_id]
        return list(self._tasks.values())

    def cancel_task(self, str task_id) -> bool:
        """Cancel a scheduled crontab task."""
        if task_id in self._tasks:
            self._tasks[task_id]["enabled"] = False
            self._tasks[task_id]["status"] = "cancelled"
            return True
        return False

    def execute_trigger(self, str task_id, object current_state=None):
        """Execute a scheduled trigger with Cython acceleration, updating state & checkpoint."""
        cdef dict task = self._tasks.get(task_id)
        cdef double now = time.time()

        if not task or not task["enabled"]:
            return {"status": "error", "message": f"Task '{task_id}' not found or disabled."}

        state = dict(current_state or {})
        state.update(task.get("state_update", {}))
        state["last_scheduled_execution"] = {
            "task_id": task_id,
            "node_id": task["node_id"],
            "timestamp": now,
            "engine": "cython",
        }

        task["last_executed_at"] = now
        task["status"] = "executed"

        if task["one_time"]:
            task["enabled"] = False
            task["status"] = "completed"

        cdef str thread_id = task["thread_id"]
        if thread_id in self._checkpoints:
            self._checkpoints[thread_id]["last_state"] = state
            self._checkpoints[thread_id]["last_execution_time"] = now

        return {
            "status": "success",
            "task_id": task_id,
            "node_id": task["node_id"],
            "updated_state": state,
            "engine": "cython",
        }

    def get_checkpoint_state(self, str thread_id):
        """Retrieve checkpoint state data for a thread."""
        return self._checkpoints.get(thread_id, {})
