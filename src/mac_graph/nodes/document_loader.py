import os
from pathlib import Path
from typing import Dict, Any
from mac_graph.state import GraphState


def load_documents_node(state: GraphState) -> Dict[str, Any]:
    """Node: Scans the source directory and loads all .md documents into graph state."""
    config = state.get("config", {})
    source_dir = config.get("source_dir", "data/source")

    source_path = Path(source_dir)
    documents = []
    source_files = []

    if not source_path.exists():
        return {
            "documents": [],
            "source_files": [],
            "status_message": f"Source directory '{source_dir}' does not exist.",
        }

    md_files = sorted(list(source_path.glob("*.md")))

    for filepath in md_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            source_files.append(str(filepath))
            documents.append({
                "file_path": str(filepath),
                "filename": filepath.name,
                "content": content,
            })
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")

    return {
        "documents": documents,
        "source_files": source_files,
        "status_message": f"Loaded {len(documents)} markdown documents from {source_dir}.",
    }
