# Grafin Wiki Skeleton

## Overview
Grafin is a "Coordinator of Coordinators" designed to unify multi-framework AI orchestration. It uses a declarative YAML manifest (`GraphInYAML`) to define topologies, models, and connections that can be executed across LangGraph, CrewAI, and Semantic Kernel.

## Proposed Wiki Structure

### 1. Core Architecture
- `/openwiki/architecture/overview.md`: High-level architectural vision, the "Coordinator of Coordinators" concept, and the role of `GraphInYAML`.
- `/openwiki/architecture/manifest_spec.md`: Detailed documentation of the `GraphInYAML` schema (`GraphManifest`, `NodeDefinition`, `EdgeDefinition`, `ConnectionDefinition`).
- `/openwiki/architecture/state_management.md`: How graph state and checkpoints are handled across different frameworks, including the `get_checkpoint_state` and `set_checkpoint_state` adapter methods.
- `/openwiki/architecture/cordis_event_system.md`: The Cordis `EventBus`, event lifecycle (sequential, parallel, bail), and how adapters/agents use these events for reactive orchestration.

### 2. Framework Adapters
- `/openwiki/adapters/overview.md`: The `IFrameworkAdapter` interface and the general translation process between manifests and native framework objects.
- `/openwiki/adapters/langgraph.md`: Deep dive into `LangGraphAdapter`, dynamic `StateGraph` assembly, and `resolve_code_ref`.
- `/openwiki/adapters/crewai.md`: Deep dive into `CrewAIAdapter`, task translation, ACL hooks, and `CrewAIGraphManipulationTool`.
- `/openwiki/adapters/semantic_kernel.md`: Deep dive into `SemanticKernelAdapter`, plugin generation, and `SemanticKernelFunctionFilter`.
- `/openwiki/adapters/yaml_adapter.md`: Documentation for `GraphInYAMLAdapter` for direct manifest manipulation.
- `/openwiki/adapters/cordis_ipc_bridge.md`: Documentation for `CordisIPCBridge`, explaining how Grafin bridges IPC for external coordinator processes.

### 3. Schedule Agents & Automation
- `/openwiki/agents/overview.md`: Overview of the Antigravity (AGY) SDK based agents for graph automation.
- `/openwiki/agents/reader_agent.md`: Documentation for `GraphinReaderAgent` (topology walking, schedule inspection).
- `/openwiki/agents/writer_agent.md`: Documentation for `GraphinWriterAgent` (topology mutation, task scheduling).
- `/openwiki/agents/scheduler.md`: Documentation for `CrontabScheduler` and the underlying scheduling mechanism.

### 4. Shared Infrastructure
- `/openwiki/infrastructure/connections.md`: Shared connection access points (DBs, Sockets, MCP, REST) and their lifecycle.
- `/openwiki/infrastructure/llm_registry.md`: Model definitions, provider mapping, and API key resolution (`llm.py`).
- `/openwiki/infrastructure/hitl.md`: Human-in-the-loop (HITL) dispatching via `AdaptiveCard` and the `hitl` package.

### 5. Extensibility & Skills
- `/openwiki/extensibility/skillsets.md`: The Graph Skillsets protocol, `SkillsetManager`, and topology walking capabilities.
- `/openwiki/extensibility/custom_nodes.md`: How to implement and reference custom nodes using the `code_ref` pattern.

### 6. Operations & Tooling
- `/openwiki/operations/cli.md`: Grafin CLI commands (`process`, `connections`, `skillset`).
- `/openwiki/operations/deployment.md`: Devcontainers and workspace configurations.
- `/openwiki/operations/testing.md`: Overview of the test suite and how to validate manifest changes.

## Key Workflows to Document
- **Manifest to Execution**: `GraphInYAML` -> `Adapter` -> `Executable Workflow`.
- **Dynamic Topology Mutation**: Agent/Tool -> `Adapter.manipulate_nodes_edges` -> `Manifest` -> `Re-execution`.
- **Cross-Framework State Transfer**: How state moves from a LangGraph node to a CrewAI task via the unified manifest/checkpoint system.
- **Scheduled Triggering**: `CrontabScheduler` -> `Node Execution` -> `State Update`.
