import re
from typing import Dict, Any, List
from graphin.state import GraphState, TextChunk


def split_markdown_into_sections(filename: str, content: str) -> List[TextChunk]:
    """Split a markdown string into logical semantic sections by headings (#, ##, ###) and paragraph blocks."""
    chunks: List[TextChunk] = []

    heading_pattern = re.compile(r'^(#{1,4})\s+(.+)$', re.MULTILINE)

    matches = list(heading_pattern.finditer(content))

    if not matches:
        blocks = [b.strip() for b in re.split(r'\n\s*\n', content) if b.strip()]
        for idx, block in enumerate(blocks, start=1):
            chunks.append({
                "id": f"{filename}-chunk-{idx}",
                "source_file": filename,
                "section_title": f"Paragraph {idx}",
                "content": block,
                "chunk_index": idx,
                "status": "pending",
                "human_verified": False,
            })
        return chunks

    chunk_idx = 1
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)

        heading_title = match.group(2).strip()
        section_text = content[start:end].strip()

        lines = section_text.splitlines()
        body_lines = lines[1:] if len(lines) > 1 else []
        body_content = "\n".join(body_lines).strip()

        if not body_content and i + 1 < len(matches):
            continue

        if not body_content:
            body_content = section_text

        chunks.append({
            "id": f"{filename}-chunk-{chunk_idx}",
            "source_file": filename,
            "section_title": heading_title,
            "content": body_content,
            "chunk_index": chunk_idx,
            "status": "pending",
            "human_verified": False,
        })
        chunk_idx += 1

    return chunks


def semantic_chunker_node(state: GraphState) -> Dict[str, Any]:
    """Node: Splits loaded documents into semantic text chunks."""
    documents = state.get("documents", [])
    all_chunks: List[TextChunk] = []

    for doc in documents:
        filename = doc.get("filename", "unknown.md")
        content = doc.get("content", "")
        file_chunks = split_markdown_into_sections(filename, content)
        all_chunks.extend(file_chunks)

    return {
        "chunks": all_chunks,
        "status_message": f"Split {len(documents)} documents into {len(all_chunks)} semantic chunks.",
    }
