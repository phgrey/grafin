from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ScheduleDefinition(BaseModel):
    cron: Optional[str] = Field(default=None, description="Standard 5-field cron expression (e.g., '0 0 * * *')")
    interval_seconds: Optional[int] = Field(default=None, description="Interval in seconds for periodic execution")
    one_time: bool = Field(default=False, description="True if task should execute once and be removed from crontab")
    enabled: bool = Field(default=True, description="Active toggle for scheduled task execution")


class ConnectionDefinition(BaseModel):
    id: str = Field(..., description="Unique connection access point alias/identifier")
    type: str = Field(..., description="Access point type: 'mysql', 'postgres', 'file_reference', 'unix_socket', 'chat_channel', 'mcp', 'rest'")
    endpoint: str = Field(..., description="Connection target URL, file path, socket path, or host:port")
    credentials_env: Optional[str] = Field(default=None, description="Environment variable name for authentication credentials")
    options: Dict[str, Any] = Field(default_factory=dict, description="Connection-specific options and parameters")


class WorkspaceConfig(BaseModel):
    devcontainers: List[str] = Field(default_factory=list, description="Devcontainer configuration paths or names")
    docker_containers: List[str] = Field(default_factory=list, description="Utility/logging container identifiers")
    local_cloud_models: Dict[str, str] = Field(default_factory=dict, description="Mapping of model aliases to local/cloud deployment targets")


class ModelDefinition(BaseModel):
    id: str = Field(..., description="Unique model alias/identifier in manifest")
    provider: str = Field(..., description="LLM provider: 'gemini', 'ollama', 'huggingface', 'openai'")
    model_name: str = Field(..., description="Provider-specific model name/path")
    protocol: Optional[str] = Field(default="https", description="Connection protocol: 'https', 'http', 'grpc', 'rest'")
    endpoint: Optional[str] = Field(default=None, description="API Endpoint / Base URL")
    api_key_env: Optional[str] = Field(default=None, description="Environment variable name for API key")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters (temperature, max_tokens, etc.)")


class NodeDefinition(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    type: str = Field(default="function", description="Node type: 'function', 'agent', 'tool', 'interrupt'")
    code_ref: str = Field(..., description="Python dot-notation code reference (e.g. module.path:function_name)")
    description: Optional[str] = Field(default="", description="Human readable node description")
    schedule: Optional[ScheduleDefinition] = Field(default=None, description="Crontab or periodic trigger schedule definition")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Framework-specific metadata")


class EdgeDefinition(BaseModel):
    source: str = Field(..., description="Source node ID or '__start__'")
    target: Optional[str] = Field(default=None, description="Target node ID or '__end__'")
    condition_ref: Optional[str] = Field(
        default=None, description="Python code reference for conditional routing function"
    )
    branches: Optional[Dict[str, str]] = Field(
        default=None, description="Mapping of branch key to target node ID for conditional edges"
    )


class GraphManifest(BaseModel):
    version: str = Field(default="0.1.0", description="GraphInYAML format version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Graph metadata (name, description, author)")
    models: List[ModelDefinition] = Field(default_factory=list, description="Centralized LLM model connection definitions")
    connections: List[ConnectionDefinition] = Field(default_factory=list, description="Shared connection access points (DB, sockets, MCP, REST)")
    workspace: Optional[WorkspaceConfig] = Field(default=None, description="Devcontainers and workspace environment configurations")
    default_model_ref: Optional[str] = Field(default=None, description="ID of default model to use")
    state_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for graph state")
    nodes: List[NodeDefinition] = Field(default_factory=list, description="List of node definitions")
    edges: List[EdgeDefinition] = Field(default_factory=list, description="List of edge definitions")
    framework_configs: Dict[str, Any] = Field(
        default_factory=dict, description="Framework-specific configuration blocks (langgraph, crewai, semantic_kernel)"
    )

    def get_model(self, model_id: str) -> Optional[ModelDefinition]:
        """Find a model definition by its ID."""
        for m in self.models:
            if m.id == model_id:
                return m
        return None

    def get_connection(self, connection_id: str) -> Optional[ConnectionDefinition]:
        """Find a connection definition by its ID."""
        for c in self.connections:
            if c.id == connection_id:
                return c
        return None

    def get_node(self, node_id: str) -> Optional[NodeDefinition]:
        """Find a node definition by its ID."""
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def add_node(self, node: NodeDefinition) -> None:
        """Add or update a node in the manifest."""
        for i, n in enumerate(self.nodes):
            if n.id == node.id:
                self.nodes[i] = node
                return
        self.nodes.append(node)

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and its connected edges from the manifest."""
        initial_count = len(self.nodes)
        self.nodes = [n for n in self.nodes if n.id != node_id]
        if len(self.nodes) < initial_count:
            self.edges = [
                e for e in self.edges
                if e.source != node_id and e.target != node_id and (not e.branches or node_id not in e.branches.values())
            ]
            return True
        return False
