# Grafin (GraphIn)

**Grafin** is the **Coordinator of Coordinators** — a framework-agnostic, manifest-driven workspace and orchestration protocol connecting **LangGraph**, **CrewAI**, and **Semantic Kernel** into a unified multi-framework ecosystem.

Grafin bridges orchestrators by using **`GraphInYAML`** (`graphin.yaml` / `*.graphin.yaml`) as the single source of truth for graph topologies, models, shared connection access points, skillsets, and devcontainers.

---

## Core Capabilities

- **Coordinator of Coordinators**: Single unified protocol enabling seamless translation and execution across:
  - **LangGraph**: Compiled `StateGraph` workflows ("Graph Frontend").
  - **CrewAI**: Task execution, agent roles, and ACL hooks ("Graph Frontend+").
  - **Semantic Kernel**: AI service registries, plugins, and execution filters ("Graph Backend").
  - **GraphInYAML**: Declarative YAML manifest specification.
- **Shared Connections & Access Points**: Connects nodes to shared resources:
  - Relational & NoSQL Databases (e.g. MySQL, PostgreSQL).
  - Inter-Process Communication (Unix domain sockets, TCP pipes, file references).
  - Chat channels & Adaptive Card HITL dispatchers.
  - Model / MCP / REST endpoints.
- **Graph Skillsets**: Standardized skill-sharing protocol for inspecting, walking, and mutating graph topology and state across all frameworks.
- **Crontab-Based Schedule Agents**: Autonomous schedule agents (**`GraphinReaderAgent`** and **`GraphinWriterAgent`**) powered by Google Antigravity (AGY) SDK for walking graphs and executing crontab background tasks.
- **Developer Workspace & Devcontainers**: Integrated devcontainer environment configurations (`workspace`, `environment`, `devcontainers`) for local and cloud workflows.

---

## `GraphInYAML` Manifest Architecture

A `graphin.yaml` manifest configures all models, nodes, edges, shared connections, and framework settings:

```yaml
version: "0.1.0"
metadata:
  name: "grafin_core_workflow"
  description: "Grafin Coordinator of Coordinators Workflow"

models:
  - id: "gemini_flash"
    provider: "gemini"
    model_name: "gemini-1.5-flash"
    api_key_env: "GEMINI_API_KEY"

connections:
  - id: "main_database"
    type: "mysql"
    endpoint: "localhost:3306"
    credentials_env: "DB_PASSWORD"

  - id: "local_pipe"
    type: "unix_socket"
    endpoint: "/tmp/grafin.sock"

nodes:
  - id: "stem_classifier"
    type: "function"
    code_ref: "examples.stem_markdown_processor.nodes.stem_classifier:stem_classifier_node"
    schedule:
      cron: "0 0 * * *"
      one_time: false
      enabled: true

edges:
  - source: "__start__"
    target: "stem_classifier"
```

---

## Quick Start

### Installation

```bash
# Clone and enter directory
cd valiant-kepler

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Grafin package in editable mode
pip install -e ".[dev]"
```

### CLI Engine Execution

Run the Grafin CLI processor on an example manifest:

```bash
graphin process --manifest examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml
```

### Single Orchestrator Experiment

Run all 4 phases of the multi-framework experiment (LangGraph -> CrewAI -> Semantic Kernel -> Schedule Agents):

```bash
python examples/stem_markdown_processor/run_experiment.py
```

### Running Tests

Execute the 100% offline automated unit test suite:

```bash
pytest tests/ -v
```
