import pytest
from graphin.manifest.schema import GraphManifest, ConnectionDefinition, WorkspaceConfig


def test_connections_and_workspace_schema():
    manifest = GraphManifest(
        version="0.1.0",
        metadata={"name": "connection_test"},
        connections=[
            ConnectionDefinition(
                id="main_db",
                type="mysql",
                endpoint="localhost:3306",
                credentials_env="DB_PASS",
            ),
            ConnectionDefinition(
                id="unix_pipe",
                type="unix_socket",
                endpoint="/tmp/grafin.sock",
            ),
        ],
        workspace=WorkspaceConfig(
            devcontainers=[".devcontainer/devcontainer.json"],
            docker_containers=["grafin_logs"],
            local_cloud_models={"primary": "gemini-1.5-flash"},
        ),
    )

    assert len(manifest.connections) == 2
    c1 = manifest.get_connection("main_db")
    assert c1 is not None
    assert c1.type == "mysql"

    c2 = manifest.get_connection("unix_pipe")
    assert c2 is not None
    assert c2.type == "unix_socket"

    assert manifest.workspace is not None
    assert len(manifest.workspace.devcontainers) == 1
    assert manifest.workspace.local_cloud_models["primary"] == "gemini-1.5-flash"
