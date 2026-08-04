# GitHub Agent Skillset Specification

The **GitHub Agent Skillset** defines the standardized protocol and API operations for AI agents executing **GitHub Flow** within **GraphIn** workflows (LangGraph, CrewAI, Semantic Kernel, and Google AGY Schedule Agents).

---

## Core GitHub Flow Principles for AI Agents

1. **Branching**: Agents create feature or incident branches from `main` or `release` (e.g. `feature/scrum-task-101`, `incident/fix-budget-alert`).
2. **Committing**: Agents commit code changes, documentation artifacts, and test reports with clear commit messages.
3. **Pull Requests**: Agents open Pull Requests (PRs) detailing proposed changes, linked SCRUM tasks, and automated test results.
4. **Code Review & Automated Approval**: Specialist agents or human reviewers inspect PRs, enforce Access Control Lists (ACL), and approve or request changes.
5. **Merging**: Upon approval, agents merge PRs into `main` and clean up feature branches.

---

## Skillset Operations & API Interface

### `create_branch`
- **Parameters**:
  - `repo`: str (Repository identifier, e.g. `phgrey/grafin`)
  - `branch_name`: str (Target branch name, e.g. `feature/sprint-task-1`)
  - `base_branch`: str (Base branch, default: `main`)
- **Returns**: `{"status": "success", "branch_name": str, "commit_sha": str}`

### `commit_files`
- **Parameters**:
  - `repo`: str
  - `branch_name`: str
  - `file_changes`: Dict[str, str] (Mapping of file paths to content)
  - `commit_message`: str
- **Returns**: `{"status": "success", "commit_sha": str, "files_committed": List[str]}`

### `create_pull_request`
- **Parameters**:
  - `repo`: str
  - `title`: str
  - `body`: str
  - `head_branch`: str
  - `base_branch`: str
- **Returns**: `{"status": "success", "pr_number": int, "pr_url": str}`

### `review_and_merge_pr`
- **Parameters**:
  - `repo`: str
  - `pr_number`: int
  - `reviewer_role`: str (e.g. `admin`, `auditor`)
  - `action`: str (`approve`, `request_changes`, `merge`)
- **Returns**: `{"status": "success", "action": str, "merged": bool}`

---

## `GraphInYAML` Node Binding Example

```yaml
nodes:
  - id: "github_flow_manager"
    type: "agent"
    code_ref: "graphin.agents.github_agent:github_agent_node"
    description: "Manages feature branch creation, commits, and Pull Requests"
    metadata:
      repo: "phgrey/grafin"
      base_branch: "main"
```
