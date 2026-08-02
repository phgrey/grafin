import os
import pytest
from graphin.manifest.schema import GraphManifest, ModelDefinition
from graphin.manifest.loader import load_manifest_from_yaml
from graphin.llm import resolve_api_key, get_llm_for_model_def
from graphin.adapters.crewai_adapter import CrewAIAdapter
from graphin.adapters.semantic_kernel_adapter import SemanticKernelAdapter


def test_model_definition_schema():
    manifest = load_manifest_from_yaml("graphin.yaml")
    assert len(manifest.models) == 3
    assert manifest.default_model_ref == "gemini_flash"

    gemini_m = manifest.get_model("gemini_flash")
    assert gemini_m is not None
    assert gemini_m.provider == "gemini"
    assert gemini_m.model_name == "gemini-1.5-flash"
    assert gemini_m.protocol == "https"
    assert gemini_m.api_key_env == "GEMINI_API_KEY"

    hf_m = manifest.get_model("hf_mistral")
    assert hf_m is not None
    assert hf_m.provider == "huggingface"
    assert hf_m.api_key_env == "HUGGINGFACE_API_KEY"


def test_api_key_env_resolution():
    # Set env vars for testing
    os.environ["TEST_GEMINI_KEY"] = "gemini_key_123"
    os.environ["TEST_HF_KEY"] = "hf_key_456"

    key_gemini = resolve_api_key("TEST_GEMINI_KEY", provider="gemini")
    assert key_gemini == "gemini_key_123"

    key_hf = resolve_api_key("TEST_HF_KEY", provider="huggingface")
    assert key_hf == "hf_key_456"

    # Test fallback resolution from .env (GEMINI_API_KET or GEMINI_API_KEY, HUGGINGFACE_API_KEY)
    env_hf = resolve_api_key("HUGGINGFACE_API_KEY", provider="huggingface")
    assert env_hf is not None and env_hf.startswith("hf_")


def test_crewai_adapter_model_adoption():
    manifest = load_manifest_from_yaml("graphin.yaml")
    adapter = CrewAIAdapter()

    config = adapter.extract_config(manifest)
    models_cfg = config.get("models", {})

    assert "gemini_flash" in models_cfg
    assert models_cfg["gemini_flash"]["model"] == "gemini/gemini-1.5-flash"
    assert models_cfg["gemini_flash"]["protocol"] == "https"

    assert "hf_mistral" in models_cfg
    assert models_cfg["hf_mistral"]["model"] == "huggingface/mistralai/Mistral-7B-Instruct-v0.2"


def test_semantic_kernel_adapter_model_adoption():
    manifest = load_manifest_from_yaml("graphin.yaml")
    adapter = SemanticKernelAdapter()

    config = adapter.extract_config(manifest)
    ai_services = config.get("ai_services", {})

    assert "gemini_flash" in ai_services
    assert ai_services["gemini_flash"]["provider"] == "gemini"
    assert ai_services["gemini_flash"]["ai_model_id"] == "gemini-1.5-flash"

    assert "hf_mistral" in ai_services
    assert ai_services["hf_mistral"]["provider"] == "huggingface"
    assert ai_services["hf_mistral"]["ai_model_id"] == "mistralai/Mistral-7B-Instruct-v0.2"


def test_llm_factory_for_model_def():
    model_def = ModelDefinition(
        id="test_ollama",
        provider="ollama",
        model_name="llama3.1",
        endpoint="http://localhost:11434",
        protocol="http",
        api_key_env="OLLAMA_API_KEY",
        parameters={"temperature": 0.1},
    )

    llm = get_llm_for_model_def(model_def)
    assert llm is not None
