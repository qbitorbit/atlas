"""Test LLM connection - Checkpoint 1.1"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm.client import get_llm_client
from llm import config


def test_llm_connection():
    """Test basic LLM connection and response."""
    print("Testing LLM connection...")
    print(f"Base URL: {config.LLM_BASE_URL}")
    print(f"Model: {config.DEFAULT_MODEL}")

    # Create LLM client
    try:
        llm = get_llm_client()
        print(f"✓ LLM client created")
    except Exception as e:
        print(f"❌ Failed to create LLM client: {e}")
        raise

    # Test simple query
    print("\nSending test query...")
    try:
        response = llm.invoke("Say 'Hello from Atlas!' and nothing else.")
        print(f"✓ Response received: {response.content}")
    except Exception as e:
        print(f"\n❌ Failed to get response from LLM")
        print(f"Error: {str(e)[:200]}")
        print("\nPossible issues:")
        print("1. Check if LLM server is running at http://10.202.1.3:8000")
        print("2. Verify network connectivity to 10.202.1.3")
        print("3. Ensure you're running: env -u http_proxy python tests/test_llm.py")
        print("4. Verify the model name is correct")
        raise

    print("\n✅ Checkpoint 1.1 PASSED - LLM connection successful!")
    return True


if __name__ == "__main__":
    try:
        test_llm_connection()
    except Exception as e:
        print(f"\n❌ Checkpoint 1.1 FAILED")
        sys.exit(1)
