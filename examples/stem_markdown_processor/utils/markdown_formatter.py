import json
from typing import Dict, Any, List
import yaml


def format_chunk_to_markdown(chunk: Dict[str, Any]) -> str:
    """Format a single classified chunk into a markdown string with frontmatter metadata."""
    frontmatter = {
        "id": chunk.get("id"),
        "source_file": chunk.get("source_file"),
        "section_title": chunk.get("section_title"),
        "primary_stem_domain": chunk.get("primary_domain"),
        "discipline": chunk.get("discipline"),
        "secondary_disciplines": chunk.get("secondary_disciplines", []),
        "confidence_score": chunk.get("confidence_score"),
        "classification_status": chunk.get("status", "classified"),
        "classification_reasoning": chunk.get("reasoning", ""),
        "human_verified": chunk.get("human_verified", False),
    }

    yaml_header = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True).strip()

    title = chunk.get("section_title", "Untitled Section")
    content = chunk.get("content", "").strip()

    return f"---\n{yaml_header}\n---\n\n## {title}\n\n{content}\n"


def format_document_summary(source_file: str, chunks: List[Dict[str, Any]]) -> str:
    """Generate a combined markdown document containing all processed and tagged chunks for a file."""
    lines = [
        f"# Processed Document: {source_file}\n",
        f"*Total Chunks Processed*: {len(chunks)}\n",
        "---\n",
    ]

    for idx, chunk in enumerate(chunks, start=1):
        lines.append(f"### Section {idx}: {chunk.get('section_title', 'Untitled')}")
        lines.append(f"- **Primary STEM Domain**: {chunk.get('primary_domain', 'Unknown')}")
        lines.append(f"- **Discipline**: `{chunk.get('discipline', 'Unclassified')}`")
        lines.append(f"- **Confidence Score**: `{chunk.get('confidence_score', 0.0):.2f}`")
        if chunk.get("human_verified"):
            lines.append(f"- **User Verified**: Yes ✅")
        lines.append(f"- **Reasoning**: {chunk.get('reasoning', '')}")
        lines.append("\n```markdown")
        lines.append(chunk.get("content", "").strip())
        lines.append("```\n")
        lines.append("---\n")

    return "\n".join(lines)
