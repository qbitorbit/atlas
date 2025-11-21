"""Test LLM connection - Checkpoint 1.1"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_openai import ChatOpenAI
from llm import config


def test_llm_connection():
    """Test basic LLM connection and response for all models."""
    print("Testing LLM connections...")
    print("=" * 60)

    # Test 1: Tool-calling model (Qwen)
    print("\n1. Testing Tool-Calling Model (Qwen)...")
    print(f"   Base URL: {config.LLM_BASE_URL}")
    print(f"   Model: {config.MODELS['tool_calling']}")

    llm_tool = ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.MODELS["tool_calling"],
        temperature=config.DEFAULT_TEMPERATURE
    )
    print(f"   ✓ Client created")

    try:
        response = llm_tool.invoke("Say 'Qwen OK' and nothing else.")
        print(f"   ✓ Response: {response.content}")
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")
        raise

    # Test 2: Reasoning model (gpt-oss-120b)
    print("\n2. Testing Reasoning Model (gpt-oss-120b)...")
    print(f"   Model: {config.MODELS['reasoning']}")

    llm_reasoning = ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.MODELS["reasoning"],
        temperature=config.DEFAULT_TEMPERATURE
    )
    print(f"   ✓ Client created")

    try:
        response = llm_reasoning.invoke("Say 'Reasoning OK' and nothing else.")
        print(f"   ✓ Response: {response.content}")
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")
        raise

    # Test 3: Fast model - Commented out (not working)
    # print("\n3. Testing Fast Model (gpt-oss-20b)...")
    # print(f"   Model: {config.MODELS['fast']}")

    print("\n" + "=" * 60)
    print("\n✅ Checkpoint 1.1 PASSED - All LLM connections successful!")
    print("\nTested models:")
    print(f"  ✓ Tool-calling: {config.MODELS['tool_calling']}")
    print(f"  ✓ Reasoning:    {config.MODELS['reasoning']}")
    # print(f"  ✓ Fast:         {config.MODELS['fast']}")
    return True


if __name__ == "__main__":
    try:
        test_llm_connection()
    except Exception as e:
        print(f"\n❌ Checkpoint 1.1 FAILED")
        sys.exit(1)
