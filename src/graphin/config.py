import os
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class AppConfig(BaseModel):
    provider: str = Field(default="gemini", description="LLM provider: 'gemini' or 'ollama'")
    source_dir: str = Field(default="data/source", description="Source directory for input files")
    output_dir: str = Field(default="data/results", description="Output directory for results")
    confidence_threshold: float = Field(
        default=0.75, description="Confidence threshold score (0.0 to 1.0)"
    )

    gemini_model: str = Field(default="gemini-1.5-flash", description="Gemini model name")
    gemini_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY"), description="Gemini API Key"
    )

    ollama_model: str = Field(default="llama3.1", description="Ollama model name")
    ollama_base_url: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        description="Ollama base API URL",
    )
    ollama_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OLLAMA_API_KEY"), description="Ollama API Key (if required)"
    )


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load GraphIn configuration from a YAML file, environment variables, and defaults."""
    config_dict = {}

    target_path = Path(config_path) if config_path else Path("config.yaml")
    if target_path.exists():
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                if isinstance(content, dict):
                    config_dict = content
        except Exception as e:
            print(f"Warning: Could not read config file at {target_path}: {e}")

    if os.getenv("GRAPHIN_PROVIDER"):
        config_dict["provider"] = os.getenv("GRAPHIN_PROVIDER")
    if os.getenv("GRAPHIN_CONFIDENCE_THRESHOLD"):
        try:
            config_dict["confidence_threshold"] = float(os.getenv("GRAPHIN_CONFIDENCE_THRESHOLD"))
        except ValueError:
            pass

    return AppConfig(**config_dict)
