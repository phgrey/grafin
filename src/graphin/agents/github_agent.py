import time
import uuid
from typing import Dict, Any, List, Optional
from graphin.state import GraphState


class GitHubAgent:
    """GitHub Agent managing GitHub Flow operations (branches, commits, pull requests, reviews)."""

    def __init__(self, repo: str = "phgrey/grafin", default_branch: str = "main"):
        self.repo = repo
        self.default_branch = default_branch
        self._branches: Dict[str, str] = {default_branch: "sha_main_001"}
        self._commits: List[Dict[str, Any]] = []
        self._pull_requests: Dict[int, Dict[str, Any]] = {}
        self._pr_counter = 100

    def create_branch(self, branch_name: str, base_branch: Optional[str] = None) -> Dict[str, Any]:
        """Create a new feature or incident branch."""
        base = base_branch or self.default_branch
        base_sha = self._branches.get(base, "sha_base_001")
        new_sha = f"sha_{uuid.uuid4().hex[:7]}"
        self._branches[branch_name] = new_sha

        return {
            "status": "success",
            "repo": self.repo,
            "branch_name": branch_name,
            "base_branch": base,
            "commit_sha": new_sha,
        }

    def commit_files(self, branch_name: str, file_changes: Dict[str, str], commit_message: str) -> Dict[str, Any]:
        """Commit files to a target branch."""
        if branch_name not in self._branches:
            self.create_branch(branch_name)

        commit_sha = f"commit_{uuid.uuid4().hex[:7]}"
        self._branches[branch_name] = commit_sha

        commit_record = {
            "commit_sha": commit_sha,
            "branch_name": branch_name,
            "message": commit_message,
            "files": list(file_changes.keys()),
            "timestamp": time.time(),
        }
        self._commits.append(commit_record)

        return {
            "status": "success",
            "commit_sha": commit_sha,
            "files_committed": list(file_changes.keys()),
            "branch_name": branch_name,
        }

    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: Optional[str] = None) -> Dict[str, Any]:
        """Open a new Pull Request."""
        base = base_branch or self.default_branch
        self._pr_counter += 1
        pr_number = self._pr_counter
        pr_url = f"https://github.com/{self.repo}/pull/{pr_number}"

        pr_record = {
            "pr_number": pr_number,
            "title": title,
            "body": body,
            "head_branch": head_branch,
            "base_branch": base,
            "url": pr_url,
            "status": "open",
            "created_at": time.time(),
            "reviews": [],
        }
        self._pull_requests[pr_number] = pr_record

        return {
            "status": "success",
            "pr_number": pr_number,
            "pr_url": pr_url,
            "title": title,
            "head_branch": head_branch,
            "base_branch": base,
        }

    def review_and_merge_pr(self, pr_number: int, reviewer_role: str = "admin", action: str = "approve") -> Dict[str, Any]:
        """Review and merge an open Pull Request."""
        pr = self._pull_requests.get(pr_number)
        if not pr:
            return {"status": "error", "message": f"PR #{pr_number} not found."}

        pr["reviews"].append({"reviewer": reviewer_role, "action": action, "timestamp": time.time()})

        if action == "approve" or action == "merge":
            pr["status"] = "merged"
            head_sha = self._branches.get(pr["head_branch"], "sha_head_merged")
            self._branches[pr["base_branch"]] = head_sha
            return {
                "status": "success",
                "pr_number": pr_number,
                "action": action,
                "merged": True,
                "target_branch": pr["base_branch"],
            }
        elif action == "request_changes":
            pr["status"] = "changes_requested"
            return {
                "status": "success",
                "pr_number": pr_number,
                "action": action,
                "merged": False,
            }

        return {"status": "error", "message": f"Unrecognized action '{action}'."}


def github_agent_node(state: GraphState) -> Dict[str, Any]:
    """LangGraph Node Callable: Executes GitHub Flow operations for SCRUM sprint tasks."""
    sprint_tasks = state.get("classified_chunks", []) or state.get("pending_reviews", [])
    task_name = sprint_tasks[0].get("section_title", "scrum-feature") if sprint_tasks else "scrum-task-001"
    slug = task_name.lower().replace(" ", "-")[:25]

    branch_name = f"feature/{slug}"
    gh_agent = GitHubAgent(repo="phgrey/grafin", default_branch="main")

    # 1. Create Feature Branch
    b_res = gh_agent.create_branch(branch_name=branch_name)

    # 2. Commit Task Artifacts
    c_res = gh_agent.commit_files(
        branch_name=branch_name,
        file_changes={"sprint_task.md": f"# {task_name}\n\nAutomated commit by GitHubAgent."},
        commit_message=f"feat(scrum): implement {task_name}",
    )

    # 3. Open Pull Request
    pr_res = gh_agent.create_pull_request(
        title=f"Feat: Implement {task_name}",
        body=f"Automated PR created by GitHubAgent for SCRUM task: {task_name}.",
        head_branch=branch_name,
        base_branch="main",
    )

    # Update state
    updated_prs = list(state.get("saved_results", []))
    updated_prs.append(pr_res["pr_url"])

    return {
        "saved_results": updated_prs,
        "status_message": f"GitHub Flow executed: Created branch '{branch_name}' and opened PR #{pr_res['pr_number']} ({pr_res['pr_url']}).",
        "github_flow_data": {
            "branch_name": branch_name,
            "pr_number": pr_res["pr_number"],
            "pr_url": pr_res["pr_url"],
            "commit_sha": c_res["commit_sha"],
        },
    }
