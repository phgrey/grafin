import json
from pathlib import Path
from typing import Dict, Any, List
from mac_graph.state import GraphState, TextChunk
from mac_graph.utils.markdown_formatter import format_chunk_to_markdown, format_document_summary


def save_results_node(state: GraphState) -> Dict[str, Any]:
    """Node: Saves classified and human-verified chunks to the output directory as Markdown and JSON."""
    config = state.get("config", {})
    output_dir = config.get("output_dir", "data/results")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    classified_chunks: List[TextChunk] = state.get("classified_chunks", [])
    saved_files: List[str] = []

    # Group chunks by source_file
    chunks_by_file: Dict[str, List[TextChunk]] = {}
    for chunk in classified_chunks:
        src = chunk.get("source_file", "unknown.md")
        if src not in chunks_by_file:
            chunks_by_file[src] = []
        chunks_by_file[src].append(chunk)

    # 1. Save aggregated summary files per source document
    for src_file, chunks in chunks_by_file.items():
        base_name = Path(src_file).stem
        out_file_name = f"{base_name}_tagged.md"
        out_file_path = output_path / out_file_name

        document_markdown = format_document_summary(src_file, chunks)
        with open(out_file_path, "w", encoding="utf-8") as f:
            f.write(document_markdown)
        saved_files.append(str(out_file_path))

    # 2. Save individual chunk files with frontmatter in chunks/ subdirectory
    chunks_subdir = output_path / "chunks"
    chunks_subdir.mkdir(parents=True, exist_ok=True)

    for chunk in classified_chunks:
        chunk_id = chunk.get("id", "chunk")
        chunk_file_path = chunks_subdir / f"{chunk_id}.md"
        chunk_markdown = format_chunk_to_markdown(chunk)
        with open(chunk_file_path, "w", encoding="utf-8") as f:
            f.write(chunk_markdown)
        saved_files.append(str(chunk_file_path))

    # 3. Save master JSON report
    report_path = output_path / "classification_summary.json"
    summary_data = {
        "total_chunks": len(classified_chunks),
        "source_documents_count": len(chunks_by_file),
        "saved_files_count": len(saved_files),
        "chunks": classified_chunks,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    saved_files.append(str(report_path))

    return {
        "saved_results": saved_files,
        "status_message": f"Successfully saved {len(classified_chunks)} tagged chunks across {len(chunks_by_file)} files to '{output_dir}'.",
    }
