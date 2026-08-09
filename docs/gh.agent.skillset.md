Here is a complete, production-ready **Open Agent Skill** (`SKILL.md` specification) for a GitHub Agent. It follows the open **Agent Skills Standard** (supported across OpenAI, GitHub Copilot CLI/VS Code, Claude Code, Codex, and Cursor) and relies **exclusively on shell scripts using `gh` (GitHub CLI) and `git`** without any MCP dependency.

---

### Skill Directory Structure

Create the following folder structure in your repository under `.github/skills/github-agent/` (for project-wide scope) or `~/.agents/skills/github-agent/` (for user-wide scope):

```text
github-agent/
├── SKILL.md
└── scripts/
    ├── repo_overview.sh
    ├── issue_manager.sh
    ├── pr_workflow.sh
    └── ci_status.sh
```

---

### 1. `SKILL.md` (Skill Manifest & Instructions)

```markdown
---
name: github-agent
description: 'Perform standard GitHub and Git management tasks using only gh CLI and git console tools. Use when asked to inspect repository status, manage issues, triage tasks, run PR lifecycles, or monitor CI workflows without MCP.'
allowed-tools: Bash(gh:*) Bash(git:*) Bash(./scripts/*) Read
---

# GitHub & Git Agent Skill

This skill provides deterministic bash scripts powered by `gh` (GitHub CLI) and `git` to manage common repository tasks.

## Quick Reference / Commands Matrix

| Task | Script Command | Description |
| :--- | :--- | :--- |
| Repository Overview | `./scripts/repo_overview.sh` | Get repo info, branch, open PRs/Issues summary |
| Issue List | `./scripts/issue_manager.sh list [limit]` | List open issues |
| Create Issue | `./scripts/issue_manager.sh create "title" "body" [labels]` | Create a new issue |
| PR Lifecycle | `./scripts/pr_workflow.sh create-pr "branch" "title" "body"` | Create branch, push, and open PR |
| PR Checkout & Test | `./scripts/pr_workflow.sh checkout <pr-number>` | Checkout PR locally for review |
| PR Merge | `./scripts/pr_workflow.sh merge <pr-number> [method]` | Squash/Merge PR |
| CI Status | `./scripts/ci_status.sh` | Check workflow run statuses and print recent failures |

---

## Workflow Guidelines

1. **Pre-requisite Check**: Verify `gh auth status` before executing operations requiring GitHub API access.
2. **Deterministic Scripting**: Always run the bundled scripts in `./scripts/` instead of executing raw, inline commands when possible.
3. **Safety First**: Never force push (`git push -f`) unless explicitly requested.

---

## Error Recovery
If a script fails:
- Run `gh auth status` to check if authentication has expired.
- Check `git status` to ensure working directory state is clean.
```

---

### 2. Bundled Executable Scripts (`scripts/`)

Make sure all script files are executable (`chmod +x scripts/*.sh`).

#### `scripts/repo_overview.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== GIT REPOSITORY STATUS ==="
echo "Current Branch: $(git rev-parse --abbrev-ref HEAD)"
echo "Status:"
git status --short

echo -e "\n=== REPOSITORY DETAILS (gh) ==="
gh repo view --json name,owner,defaultBranchRef,stargazerCount --template 'Repo: {{.owner.login}}/{{.name}} | Default Branch: {{.defaultBranchRef.name}}'
echo ""

echo -e "\n=== OPEN PULL REQUESTS ==="
gh pr list --limit 5 --json number,title,author,headRefName --template '{{range .}}#{{.number}} - {{.title}} (by @{{.author.login}}) [{{.headRefName}}]{{"\n"}}{{end}}'

echo -e "\n=== OPEN ISSUES (TOP 5) ==="
gh issue list --limit 5 --json number,title,assignees,labels --template '{{range .}}#{{.number}} - {{.title}} [{{range .labels}}{{.name}} {{end}}]{{"\n"}}{{end}}'

echo -e "\n=== LATEST WORKFLOW RUNS ==="
gh run list --limit 3
```

#### `scripts/issue_manager.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-list}"

case "$ACTION" in
  list)
    LIMIT="${2:-10}"
    gh issue list --limit "$LIMIT"
    ;;
  view)
    ISSUE_NUM="${2:?Error: Issue number required}"
    gh issue view "$ISSUE_NUM"
    gh issue view "$ISSUE_NUM" --comments
    ;;
  create)
    TITLE="${2:?Error: Issue title required}"
    BODY="${3:-No description provided.}"
    LABELS="${4:-}"
    
    if [ -n "$LABELS" ]; then
      gh issue create --title "$TITLE" --body "$BODY" --label "$LABELS"
    else
      gh issue create --title "$TITLE" --body "$BODY"
    fi
    ;;
  close)
    ISSUE_NUM="${2:?Error: Issue number required}"
    REASON="${3:-completed}" # completed or not_planned
    gh issue close "$ISSUE_NUM" --reason "$REASON"
    ;;
  comment)
    ISSUE_NUM="${2:?Error: Issue number required}"
    COMMENT="${3:?Error: Comment text required}"
    gh issue comment "$ISSUE_NUM" --body "$COMMENT"
    ;;
  *)
    echo "Usage: $0 {list|view|create|close|comment} [args...]"
    exit 1
    ;;
esac
```

#### `scripts/pr_workflow.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-status}"

case "$ACTION" in
  status)
    gh pr status
    ;;
  checkout)
    PR_NUM="${2:?Error: PR number required}"
    gh pr checkout "$PR_NUM"
    ;;
  create-pr)
    BRANCH_NAME="${2:?Error: Branch name required}"
    TITLE="${3:?Error: PR title required}"
    BODY="${4:-Automated PR creation.}"
    
    # Create and checkout branch if not on it
    if [ "$(git rev-parse --abbrev-ref HEAD)" != "$BRANCH_NAME" ]; then
      git checkout -b "$BRANCH_NAME"
    fi
    
    # Push branch to remote
    git push -u origin "$BRANCH_NAME"
    
    # Create PR using gh
    gh pr create --title "$TITLE" --body "$BODY" --web=false
    ;;
  merge)
    PR_NUM="${2:?Error: PR number required}"
    METHOD="${3:-squash}" # squash, merge, or rebase
    gh pr merge "$PR_NUM" "--$METHOD" --auto --delete-branch
    ;;
  checks)
    PR_NUM="${2:?Error: PR number required}"
    gh pr checks "$PR_NUM"
    ;;
  *)
    echo "Usage: $0 {status|checkout|create-pr|merge|checks} [args...]"
    exit 1
    ;;
esac
```

#### `scripts/ci_status.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== GITHUB ACTIONS RUNS ==="
gh run list --limit 10

echo -e "\n=== CHECKING FOR FAILED RUNS ==="
FAILED_RUN=$(gh run list --status failure --limit 1 --json databaseId --jq '.[0].databaseId')

if [ -n "$FAILED_RUN" ] && [ "$FAILED_RUN" != "null" ]; then
  echo "Found failed workflow run ID: $FAILED_RUN"
  echo "Displaying failure log summary:"
  gh run view "$FAILED_RUN" --log-failed
else
  echo "No recent workflow failures found."
fi
```

---

### How to Install & Use

1. **Local Project Scope**:
   Save this folder under `.github/skills/github-agent/` in your repository.
2. **User Scope (Available in all repos)**:
   Save this folder under `~/.agents/skills/github-agent/` or `~/.copilot/skills/github-agent/`.
3. **Using GitHub CLI `gh skill` installer** (if publishing to a repo):
   ```bash
   gh skill install your-username/your-repo github-agent
   ```
4. **Execution**:
   When prompted, OpenAI agents (via OpenAI Agents SDK, Codex CLI, or ChatGPT Agent mode) will dynamically discover `SKILL.md` and trigger the appropriate shell scripts via standard command execution.