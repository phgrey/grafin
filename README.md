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

We've been recommended by jurist to categorically reject all the deductions you are attempting to charge against the deposit

First - we have to ask for a copy AVRA deposit confirmation.

Abouth the list:
 - Humidity and painting: Under Article 21 of the Spanish Urban Tenancy Act (Ley de Arrendamientos Urbanos - LAU) and established jurisprudence, structural humidity, condensation, and general preservation of the property are the exclusive responsibility of the landlord (obras de conservación). They are not attributable to the tenant and cannot legally be deducted from the security deposit.
 - Personal living expenses and temporary accommodation: Charging us for 2 months of your personal temporary studio rent has zero legal basis and violates the legal purpose and definition of a rental deposit.
 - Normal wear and tear & breakdowns: Pursuant to Articles 1561 and 1562 of the Spanish Civil Code (Código Civil), tenants are not liable for deteriorations caused by ordinary use, the passage of time, or routine maintenance of fixtures/appliances (doorknobs, AC, fridge, boiler). Furthermore, you explicitly acknowledge that certain damages occurred weeks after the keys were returned.
 - Cleaning: The apartment was returned clean and in proper condition, as documented in our exit photo report.
- AC was broken by the start - it had elecricity problem we've discussed in whatsup. Sofa was broken as well.

We also discovered violations of the LAU law on your part, so we believe we have the right to challenge your decision all the way to court. There's some sort of simplified procedure there.
 