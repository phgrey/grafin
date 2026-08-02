# Single Orchestrator Experiment

This experiment validates the **`GraphIn`** manifest translation lifecycle using the **STEM Markdown Processor** application.

We start with a native **LangGraph** workflow, export it into a `GraphInYAML` manifest (`stem_markdown_processor.graphin.yaml`), execute it via `LangGraphAdapter`, inject **CrewAI** multi-agent configuration, and inspect it via **Semantic Kernel**.

---

## Experiment Phases

1. **Phase 1: LangGraph Native Baseline & Export** (`01_langgraph_export_and_run.py`)
   - Constructs a native LangGraph workflow.
   - Populates centralized `models` definitions for **Gemini**, **Ollama**, and **HuggingFace**.
   - Exports the graph into `stem_markdown_processor.graphin.yaml`.
   - Executes baseline via `LangGraphAdapter`.

2. **Phase 2: CrewAI Injection & ACL Tool Execution** (`02_crewai_inject_and_run.py`)
   - Reads `stem_markdown_processor.graphin.yaml`.
   - Injects CrewAI tasks, roles, and model configurations (`CrewAIAdapter.inject_config()`).
   - Tests `CrewAIGraphManipulationTool` and ACL hooks (verifying role authorization).

3. **Phase 3: Semantic Kernel Inspection & Filter Execution** (`03_semantic_kernel_inspect.py`)
   - Reads `stem_markdown_processor.graphin.yaml`.
   - Injects Semantic Kernel AI service registries and plugin definitions (`SemanticKernelAdapter.inject_config()`).
   - Tests `GraphManipulationPlugin` and function execution filters.

---

## Running the Experiment

Run all phases sequentially:

```bash
python examples/stem_markdown_processor/run_experiment.py
```

Or run individual phase scripts:

```bash
python examples/stem_markdown_processor/01_langgraph_export_and_run.py
python examples/stem_markdown_processor/02_crewai_inject_and_run.py
python examples/stem_markdown_processor/03_semantic_kernel_inspect.py
```
