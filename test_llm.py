"""Test LLM connection - Checkpoint 1.1"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_openai import ChatOpenAI
from llm import config


def test_llm_connection():
    """Test basic LLM connection and response."""
    print("Testing LLM connection...")
    print(f"Base URL: {config.LLM_BASE_URL}")
    print(f"Model: {config.DEFAULT_MODEL}")
    print(f"Temperature: {config.DEFAULT_TEMPERATURE}")

    # Create LLM client directly (same as working atlas.py)
    print("\nCreating LLM client...")
    llm = ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.DEFAULT_MODEL,
        temperature=config.DEFAULT_TEMPERATURE
    )
    print(f"✓ LLM client created")

    # Test simple query
    print("\nSending test query...")
    try:
        response = llm.invoke("Say 'Hello from Atlas!' and nothing else.")
        print(f"✓ Response received: {response.content}")
    except Exception as e:
        print(f"\n❌ Failed to get response from LLM")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {str(e)[:300]}")
        print("\nDebugging info:")
        print(f"  base_url={config.LLM_BASE_URL}")
        print(f"  model={config.DEFAULT_MODEL}")
        raise

    print("\n✅ Checkpoint 1.1 PASSED - LLM connection successful!")
    return True


if __name__ == "__main__":
    try:
        test_llm_connection()
    except Exception as e:
        print(f"\n❌ Checkpoint 1.1 FAILED")
        sys.exit(1)
