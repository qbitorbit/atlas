"""Test LLM connection - Checkpoint 1.1"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm.client import get_llm_client


def test_llm_connection():
    """Test basic LLM connection and response."""
    print("Testing LLM connection...")

    # Create LLM client
    llm = get_llm_client()
    print(f"✓ LLM client created")
    print(f"  Model: {llm.model_name}")
    print(f"  Base URL: {llm.openai_api_base}")

    # Test simple query
    print("\nSending test query...")
    response = llm.invoke("Say 'Hello from Atlas!' and nothing else.")
    print(f"✓ Response received: {response.content}")

    print("\n✅ Checkpoint 1.1 PASSED - LLM connection successful!")
    return True


if __name__ == "__main__":
    try:
        test_llm_connection()
    except Exception as e:
        print(f"\n❌ Checkpoint 1.1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
