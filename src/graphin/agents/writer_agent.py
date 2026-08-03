from typing import Dict, Any, List, Optional
from graphin.manifest.schema import GraphManifest, NodeDefinition, EdgeDefinition, ScheduleDefinition
from graphin.agents.scheduler import CrontabScheduler


class GraphinWriterAgent:
    """Google Antigravity SDK Schedule Agent (Writer): Modifies graph manifest, registers crontab tasks & updates checkpoint state."""

    def __init__(self, name: str = "GraphinWriter"):
        self.name = name
        self.system_instruction = (
            "You are GraphinWriter, a Google Antigravity SDK schedule agent. "
            "You modify graph manifests, schedule nodes into crontab tasks, and update checkpoint states."
        )

    def schedule_node_task(
        self,
        manifest: GraphManifest,
        scheduler: CrontabScheduler,
        node_id: str,
        cron: Optional[str] = None,
        interval_seconds: Optional[int] = None,
        one_time: bool = False,
        enabled: bool = True,
        thread_id: str = "default_thread",
        state_update: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Attach schedule definition to a node in the manifest and register a task in the crontab scheduler."""
        node = manifest.get_node(node_id)
        if not node:
            return {"status": "error", "message": f"Node '{node_id}' not found in manifest."}

        sched_def = ScheduleDefinition(
            cron=cron,
            interval_seconds=interval_seconds,
            one_time=one_time,
            enabled=enabled,
        )
        node.schedule = sched_def

        task_id = scheduler.register_task(
            node_id=node_id,
            schedule=sched_def,
            thread_id=thread_id,
            initial_state_update=state_update,
        )

        return {
            "status": "success",
            "message": f"Node '{node_id}' scheduled successfully.",
            "task_id": task_id,
            "node_id": node_id,
            "schedule": sched_def.model_dump(),
            "thread_id": thread_id,
        }

    def mutate_graph_topology(
        self,
        manifest: GraphManifest,
        add_nodes: Optional[List[NodeDefinition]] = None,
        remove_nodes: Optional[List[str]] = None,
        add_edges: Optional[List[EdgeDefinition]] = None,
    ) -> Dict[str, Any]:
        """Add or remove nodes and edges in the graph manifest."""
        added_nodes_count = 0
        removed_nodes_count = 0
        added_edges_count = 0

        if remove_nodes:
            for nid in remove_nodes:
                if manifest.remove_node(nid):
                    removed_nodes_count += 1

        if add_nodes:
            for n in add_nodes:
                manifest.add_node(n)
                added_nodes_count += 1

        if add_edges:
            for e in add_edges:
                manifest.edges.append(e)
                added_edges_count += 1

        return {
            "status": "success",
            "added_nodes": added_nodes_count,
            "removed_nodes": removed_nodes_count,
            "added_edges": added_edges_count,
        }

    def update_checkpoint_state(
        self, scheduler: CrontabScheduler, thread_id: str, state_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update node/thread checkpoint state directly."""
        checkpoint = scheduler.get_checkpoint_state(thread_id)
        checkpoint.update(state_data)
        return {
            "status": "success",
            "thread_id": thread_id,
            "updated_checkpoint": checkpoint,
        }
