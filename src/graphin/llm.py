import os
from typing import Any, Optional
from langchain_core.language_models import BaseChatModel

from graphin.config import AppConfig
from graphin.manifest.schema import ModelDefinition


def resolve_api_key(env_var_name: Optional[str] = None, provider: str = "") -> Optional[str]:
    """Resolve API key credential from environment variables, including fallback alias checks."""
    if env_var_name and os.getenv(env_var_name):
        return os.getenv(env_var_name)

    prov = provider.lower().strip()
    if prov == "gemini":
        return os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KET")
    elif prov == "ollama":
        return os.getenv("OLLAMA_API_KEY")
    elif prov == "huggingface":
        return os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")

    return None


def get_llm_for_model_def(model_def: ModelDefinition) -> BaseChatModel:
    """Factory function to build a LangChain ChatModel driver from a ModelDefinition manifest entry."""
    provider = model_def.provider.lower().strip()
    api_key = resolve_api_key(model_def.api_key_env, provider=provider)
    params = dict(model_def.parameters)

    if provider == "gemini":
        if not api_key:
            raise ValueError(
                f"API Key missing for Gemini model '{model_def.id}'. "
                f"Please set environment variable '{model_def.api_key_env or 'GEMINI_API_KEY'}'."
            )
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            temp = params.pop("temperature", 0.1)
            return ChatGoogleGenerativeAI(
                model=model_def.model_name,
                google_api_key=api_key,
                temperature=temp,
                **params,
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

            endpoint = model_def.endpoint or "http://localhost:11434"
            temp = params.pop("temperature", 0.1)

            kwargs: dict[str, Any] = {
                "model": model_def.model_name,
                "base_url": endpoint,
                "temperature": temp,
            }
            if api_key:
                kwargs["client_kwargs"] = {"headers": {"Authorization": f"Bearer {api_key}"}}

            return ChatOllama(**kwargs)
        except ImportError:
            raise ImportError(
                "langchain-ollama or langchain-community package is not installed. Install with `pip install langchain-ollama`."
            )

    elif provider in ("huggingface", "hf"):
        if not api_key:
            raise ValueError(
                f"API Key missing for HuggingFace model '{model_def.id}'. "
                f"Please set environment variable '{model_def.api_key_env or 'HUGGINGFACE_API_KEY'}'."
            )
        try:
            try:
                from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
                endpoint_url = model_def.endpoint or f"https://api-inference.huggingface.co/models/{model_def.model_name}"

                llm_endpoint = HuggingFaceEndpoint(
                    endpoint_url=endpoint_url,
                    huggingfacehub_api_token=api_key,
                    task="text-generation",
                    **params,
                )
                return ChatHuggingFace(llm=llm_endpoint)

            except Exception as ex:
                from langchain_community.llms import HuggingFaceEndpoint
                endpoint_url = model_def.endpoint or f"https://api-inference.huggingface.co/models/{model_def.model_name}"
                return HuggingFaceEndpoint(
                    repo_id=model_def.model_name,
                    huggingfacehub_api_token=api_key,
                    **params,
                )  # type: ignore

        except ImportError:
            raise ImportError(
                "langchain-huggingface package is not installed. Install with `pip install langchain-huggingface huggingface_hub`."
            )

    else:
        raise ValueError(
            f"Unsupported LLM provider '{provider}' in model '{model_def.id}'. "
            "Supported providers: 'gemini', 'ollama', 'huggingface'."
        )


def get_llm_client(config: AppConfig) -> BaseChatModel:
    """Legacy factory function to initialize Chat model from AppConfig."""
    model_def = ModelDefinition(
        id=f"config_{config.provider}",
        provider=config.provider,
        model_name=config.gemini_model if config.provider == "gemini" else config.ollama_model,
        endpoint=config.ollama_base_url if config.provider == "ollama" else None,
        api_key_env="GEMINI_API_KEY" if config.provider == "gemini" else "OLLAMA_API_KEY",
        parameters={"temperature": 0.1},
    )
    return get_llm_for_model_def(model_def)
