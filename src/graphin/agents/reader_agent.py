import json
from typing import Dict, Any, List, Optional
from graphin.manifest.schema import GraphManifest
from graphin.agents.scheduler import CrontabScheduler


class GraphinReaderAgent:
    """Google Antigravity SDK Schedule Agent (Reader): Walks graph topology, inspects node schedules & reads checkpoint state."""

    def __init__(self, name: str = "GraphinReader"):
        self.name = name
        self.system_instruction = (
            "You are GraphinReader, a Google Antigravity SDK schedule agent. "
            "You walk graph manifest topologies, inspect scheduled crontab tasks, and read checkpoint states."
        )

    def walk_graph(self, manifest: GraphManifest) -> Dict[str, Any]:
        """Walk manifest topology, returning node sequence, code references, and edge paths."""
        nodes_summary = []
        for n in manifest.nodes:
            sched_str = "None"
            if n.schedule:
                sched_str = f"cron='{n.schedule.cron}', one_time={n.schedule.one_time}, enabled={n.schedule.enabled}"

            nodes_summary.append({
                "id": n.id,
                "type": n.type,
                "code_ref": n.code_ref,
                "description": n.description,
                "schedule": sched_str,
            })

        edges_summary = []
        for e in manifest.edges:
            edges_summary.append({
                "source": e.source,
                "target": e.target,
                "condition_ref": e.condition_ref,
                "branches": e.branches,
            })

        return {
            "agent_name": self.name,
            "manifest_name": manifest.metadata.get("name", "unnamed_graph"),
            "node_count": len(manifest.nodes),
            "edge_count": len(manifest.edges),
            "nodes": nodes_summary,
            "edges": edges_summary,
            "models_count": len(manifest.models),
        }

    def inspect_schedule(self, scheduler: CrontabScheduler, thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Inspect all crontab schedule tasks registered in the scheduler."""
        return scheduler.list_tasks(thread_id=thread_id)

    def read_checkpoint_state(self, scheduler: CrontabScheduler, thread_id: str) -> Dict[str, Any]:
        """Read checkpoint state for a specific thread execution."""
        return scheduler.get_checkpoint_state(thread_id)
