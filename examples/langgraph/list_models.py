"""
Google GenAI Model Inspector
============================
Queries Google GenAI ModelService to list available models, test which ones
respond to content generation, and display recommended model identifiers for LangChain / DeepAgents.

Usage:
    uv run python examples/langgraph/list_models.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def list_and_test_google_models():
    from google import genai

    api_key = (
        os.getenv("GOOGLE_API_KEY")
        # or os.getenv("GOOGLE_API_KEY")
        # or os.getenv("GEMINI_API_KET")
    )
    if not api_key:
        print("❌ Error: No Google/Gemini API key found in environment (.env).")
        print("Please set GEMINI_API_KEY or GOOGLE_API_KEY.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    print("=" * 70)
    print("🔍 Fetching available models from Google ModelService...")
    print("=" * 70)

    models = list(client.models.list())
    all_model_names = [m.name.replace("models/", "") for m in models]

    print(f"Total models in catalogue: {all_model_names}\n")

    return 0
    test_candidates = [
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.1-pro-preview",
        "gemma-4-31b-it",
        "gemini-2.5-flash",
        "gemini-1.5-flash",
    ]

    print("🧪 Testing active availability with generate_content:")
    print("-" * 70)

    active_models = []
    for model_name in test_candidates:
        try:
            res = client.models.generate_content(
                model=model_name,
                contents="Reply with: OK",
            )
            reply = res.text.strip() if res.text else "OK"
            print(f"  ✅ {model_name:<25} -> {reply}")
            active_models.append(model_name)
        except Exception as e:
            err_msg = str(e)
            if "is no longer available" in err_msg:
                print(f"  ⚠️  {model_name:<25} -> Deprecated (sunset)")
            elif "not found" in err_msg.lower():
                print(f"  ❌ {model_name:<25} -> Not Found / Unsupported")
            else:
                print(f"  ❌ {model_name:<25} -> {err_msg[:60]}...")

    print("\n" + "=" * 70)
    print("💡 Recommended model configuration for create_deep_agent:")
    print("=" * 70)
    for model in active_models:
        print(f'   👉 model="google_genai:{model}"')
    print("=" * 70)


if __name__ == "__main__":
    list_and_test_google_models()
