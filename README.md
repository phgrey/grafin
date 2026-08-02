# GraphIn

**GraphIn** is a framework-agnostic, manifest-driven execution graph engine for building, running, and managing AI agent workflows across **LangGraph**, **CrewAI**, and **Semantic Kernel** (Python).

Graph workflows are defined in the **`GraphInYAML`** format (`graphin.yaml` or `*.graphin.yaml`).

## Features

- **`GraphInYAML` Format**: Declarative YAML manifest specification (`graphin.yaml`) serving as the single source of truth for graph topology, nodes (`code_ref`), edges, state schema, and framework settings.
- **Multi-Framework Adapters**:
  - **LangGraph Adapter**: Executable build engine & graph exporter ("Graph Frontend").
  - **CrewAI Adapter**: Exposes graph node/edge manipulation tools (`CrewAIGraphManipulationTool`) with support for CrewAI **Hooks** and Access Control Lists (ACL) ("Graph Frontend+").
  - **Semantic Kernel Adapter**: Exposes graph manipulation plugins (`GraphManipulationPlugin`) with **Function Execution Filters** ("Graph Backend").
  - **GraphInYAML Adapter**: Native manifest loader and serializer.
- **Centralized HITL & Adaptive Cards**: Captures graph execution interrupts and formats them into Microsoft **Adaptive Cards** v1.4 JSON payloads for user interaction in chat channels.
- **Modular Examples**: Example workflows (such as the STEM Markdown Processor) are isolated in `examples/`.

## Installation & Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install GraphIn package
pip install -e ".[dev]"
```

## Quick Start

Run the `graphin` CLI engine on the STEM Markdown Processor example:

```bash
graphin process --manifest examples/stem_markdown_processor/stem_markdown_processor.graphin.yaml --source-dir examples/stem_markdown_processor/data/source --output-dir examples/stem_markdown_processor/data/results
```

## Running Tests

Run the test suite:

```bash
pytest tests/ -v
```
