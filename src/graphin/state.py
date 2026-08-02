from typing import TypedDict, List, Dict, Any, Optional


class TextChunk(TypedDict, total=False):
    id: str
    source_file: str
    section_title: str
    content: str
    chunk_index: int
    primary_domain: Optional[str]
    discipline: Optional[str]
    secondary_disciplines: List[str]
    confidence_score: float
    reasoning: str
    status: str
    human_verified: bool


class GraphState(TypedDict, total=False):
    source_files: List[str]
    documents: List[Dict[str, Any]]
    chunks: List[TextChunk]
    classified_chunks: List[TextChunk]
    pending_reviews: List[TextChunk]
    current_review_chunk: Optional[TextChunk]
    user_override: Optional[Dict[str, Any]]
    saved_results: List[str]
    config: Dict[str, Any]
    status_message: str
