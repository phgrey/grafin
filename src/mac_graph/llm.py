import os
from typing import Any, Optional
from langchain_core.language_models import BaseChatModel
from mac_graph.config import AppConfig


def get_llm_client(config: AppConfig) -> BaseChatModel:
    """Factory function to initialize Gemini 1.5 or Ollama Chat Model based on configuration."""
    provider = config.provider.lower().strip()

    if provider == "gemini":
        api_key = config.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable or config field is missing. "
                "Please set GEMINI_API_KEY in your .env file or pass provider='ollama'."
            )
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=config.gemini_model,
                google_api_key=api_key,
                temperature=0.1,
            )
        except ImportError:
            raise ImportError(
                "langchain-google-genai package is not installed. Install with `pip install langchain-google-genai`."
            )

    elif provider == "ollama":
        try:
            try:
                from langchain_ollama import ChatOllama
            except ImportError:
                from langchain_community.chat_models import ChatOllama

            kwargs: dict[str, Any] = {
                "model": config.ollama_model,
                "base_url": config.ollama_base_url,
                "temperature": 0.1,
            }
            # Add API key header if provided
            if config.ollama_api_key:
                kwargs["client_kwargs"] = {"headers": {"Authorization": f"Bearer {config.ollama_api_key}"}}

            return ChatOllama(**kwargs)
        except ImportError:
            raise ImportError(
                "langchain-ollama or langchain-community package is not installed. Install with `pip install langchain-ollama`."
            )

    else:
        raise ValueError(f"Unsupported LLM provider: '{provider}'. Supported providers are 'gemini' and 'ollama'.")
