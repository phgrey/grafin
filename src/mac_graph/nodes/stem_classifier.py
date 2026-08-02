import json
import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from mac_graph.state import GraphState, TextChunk
from mac_graph.config import AppConfig, load_config
from mac_graph.llm import get_llm_client
from mac_graph.utils.stem_taxonomy import STEM_TAXONOMY, get_all_disciplines, get_stem_domains


class STEMClassificationOutput(BaseModel):
    primary_domain: str = Field(
        description="Top-level STEM domain: 'Science', 'Technology', 'Engineering', or 'Mathematics'"
    )
    discipline: str = Field(description="Specific subdiscipline from STEM taxonomy")
    secondary_disciplines: List[str] = Field(
        default=[], description="Secondary subdisciplines if cross-disciplinary"
    )
    confidence_score: float = Field(
        description="Confidence score between 0.0 and 1.0. Lower scores indicate ambiguity or uncertainty."
    )
    reasoning: str = Field(description="Brief rationale for the classification")


CLASSIFICATION_PROMPT = """You are an expert STEM (Science, Technology, Engineering, Mathematics) classification system.
Analyze the following text section and classify it into the most accurate STEM domain and discipline.

Target STEM Taxonomy:
{taxonomy_str}

Text Section Title: {section_title}
Text Section Content:
\"\"\"
{content}
\"\"\"

Respond strictly with valid JSON containing the following fields:
- primary_domain: string (must be one of: Science, Technology, Engineering, Mathematics)
- discipline: string (most relevant specific subfield from taxonomy)
- secondary_disciplines: array of strings (other relevant subfields, if any)
- confidence_score: float between 0.0 and 1.0 (Rate your certainty. Use < 0.70 if the text is ambiguous, interdisciplinary, or lacks clear technical context)
- reasoning: string (1-2 sentences explaining why)

JSON Output:"""


def _has_keyword(text: str, keywords: List[str]) -> bool:
    """Helper to check word-boundary matching for keywords."""
    for kw in keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def heuristic_fallback_classifier(title: str, content: str) -> STEMClassificationOutput:
    """Fallback keyword-based classifier when LLM is unavailable or for offline testing."""
    text = (title + " " + content)

    if _has_keyword(text, ["quantum", "qubit", "qubits", "physics", "relativity", "particle", "electron", "wave"]):
        return STEMClassificationOutput(
            primary_domain="Science",
            discipline="Quantum Mechanics",
            secondary_disciplines=["Physics"],
            confidence_score=0.88,
            reasoning="Detected strong physics and quantum mechanics terminology.",
        )
    elif _has_keyword(text, ["neural", "learning", "algorithm", "model", "ai", "deep learning", "transformer"]):
        return STEMClassificationOutput(
            primary_domain="Technology",
            discipline="Artificial Intelligence & Machine Learning",
            secondary_disciplines=["Computer Science"],
            confidence_score=0.90,
            reasoning="Detected AI/ML algorithms and neural network vocabulary.",
        )
    elif _has_keyword(text, ["derivative", "integral", "calculus", "equation", "matrix", "vector", "theorem"]):
        return STEMClassificationOutput(
            primary_domain="Mathematics",
            discipline="Calculus & Analysis",
            secondary_disciplines=["Applied Mathematics"],
            confidence_score=0.92,
            reasoning="Detected mathematical equations, calculus, and matrix terminology.",
        )
    elif _has_keyword(text, ["cell", "dna", "rna", "respiration", "protein", "biological", "gene", "glycolysis"]):
        return STEMClassificationOutput(
            primary_domain="Science",
            discipline="Biology",
            secondary_disciplines=["Biochemistry"],
            confidence_score=0.85,
            reasoning="Detected biological cell structures and genetic terms.",
        )
    else:
        # Ambiguous case to trigger human review threshold test!
        return STEMClassificationOutput(
            primary_domain="Technology",
            discipline="Information Systems",
            secondary_disciplines=["Data Science & Analytics"],
            confidence_score=0.55,  # Intentionally low to test HITL interrupt logic
            reasoning="General technical text with mixed signals; low confidence requires user verification.",
        )


def classify_chunk(chunk: TextChunk, config: AppConfig, llm=None) -> TextChunk:
    """Classify a single text chunk using the LLM client or fallback classifier."""
    title = chunk.get("section_title", "")
    content = chunk.get("content", "")

    result: STEMClassificationOutput

    if llm is not None:
        try:
            taxonomy_str = json.dumps(STEM_TAXONOMY, indent=2)
            prompt_text = CLASSIFICATION_PROMPT.format(
                taxonomy_str=taxonomy_str, section_title=title, content=content[:2000]
            )

            response = llm.invoke(prompt_text)
            response_content = getattr(response, "content", str(response))

            # Extract JSON block
            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if json_match:
                parsed_json = json.loads(json_match.group(0))
                result = STEMClassificationOutput(**parsed_json)
            else:
                result = heuristic_fallback_classifier(title, content)
        except Exception as e:
            print(f"LLM Classification failed for '{title}': {e}. Using fallback classifier.")
            result = heuristic_fallback_classifier(title, content)
    else:
        result = heuristic_fallback_classifier(title, content)

    classified = dict(chunk)
    classified["primary_domain"] = result.primary_domain
    classified["discipline"] = result.discipline
    classified["secondary_disciplines"] = result.secondary_disciplines
    classified["confidence_score"] = float(result.confidence_score)
    classified["reasoning"] = result.reasoning

    # Threshold comparison
    threshold = config.confidence_threshold
    if classified["confidence_score"] >= threshold:
        classified["status"] = "classified"
    else:
        classified["status"] = "needs_review"

    return classified  # type: ignore


def stem_classifier_node(state: GraphState) -> Dict[str, Any]:
    """Node: Classifies all text chunks using STEM taxonomy and identifies low-confidence chunks."""
    config_dict = state.get("config", {})
    app_config = AppConfig(**config_dict)

    llm = None
    try:
        llm = get_llm_client(app_config)
    except Exception as e:
        print(f"Notice: Initializing LLM client skipped ({e}). Operating in deterministic heuristic mode.")

    chunks = state.get("chunks", [])
    classified_chunks: List[TextChunk] = []
    pending_reviews: List[TextChunk] = []

    for chunk in chunks:
        classified = classify_chunk(chunk, app_config, llm=llm)
        classified_chunks.append(classified)
        if classified.get("status") == "needs_review":
            pending_reviews.append(classified)

    return {
        "classified_chunks": classified_chunks,
        "pending_reviews": pending_reviews,
        "status_message": (
            f"Classified {len(classified_chunks)} chunks. "
            f"{len(pending_reviews)} chunks fall below confidence threshold ({app_config.confidence_threshold}) "
            f"and require user review."
        ),
    }
