from pathlib import Path
from typing import Union
import yaml
from mac_graph.manifest.schema import GraphManifest


def load_manifest_from_yaml(source: Union[str, Path]) -> GraphManifest:
    """Load and validate a GraphManifest instance from a YAML string or file path."""
    source_path = Path(source) if isinstance(source, (str, Path)) and Path(source).exists() else None

    if source_path:
        with open(source_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    else:
        # Source is a raw YAML string
        data = yaml.safe_load(str(source))

    if not isinstance(data, dict):
        raise ValueError("Invalid manifest YAML: Root must be a key-value dictionary.")

    return GraphManifest(**data)


def save_manifest_to_yaml(manifest: GraphManifest, target_path: Union[str, Path]) -> None:
    """Serialize a GraphManifest instance to a YAML file."""
    path = Path(target_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data_dict = manifest.model_dump(exclude_none=True)

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data_dict, f, sort_keys=False, allow_unicode=True, indent=2)
