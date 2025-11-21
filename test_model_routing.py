"""Test Model Routing - Checkpoint 1.2"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm.router import get_routed_llm, get_fast_llm
from llm import config


def test_model_routing():
    """Test that model routing selects correct models."""
    print("Testing Model Routing Middleware...")
    print("=" * 60)

    # Test 1: Tool calling model
    print("\n1. Testing tool-calling model selection...")
    llm_tools = get_routed_llm(use_tools=True)
    print(f"   Model selected: {llm_tools.model_name}")
    expected_tool_model = config.MODELS["tool_calling"]
    assert llm_tools.model_name == expected_tool_model, \
        f"Expected {expected_tool_model}, got {llm_tools.model_name}"
    print(f"   ✓ Correct: {expected_tool_model}")

    # Test 2: Reasoning model
    print("\n2. Testing reasoning model selection...")
    llm_reasoning = get_routed_llm(use_tools=False)
    print(f"   Model selected: {llm_reasoning.model_name}")
    expected_reasoning_model = config.MODELS["reasoning"]
    assert llm_reasoning.model_name == expected_reasoning_model, \
        f"Expected {expected_reasoning_model}, got {llm_reasoning.model_name}"
    print(f"   ✓ Correct: {expected_reasoning_model}")

    # Test 3: Fast model
    print("\n3. Testing fast model selection...")
    llm_fast = get_fast_llm()
    print(f"   Model selected: {llm_fast.model_name}")
    expected_fast_model = config.MODELS["fast"]
    assert llm_fast.model_name == expected_fast_model, \
        f"Expected {expected_fast_model}, got {llm_fast.model_name}"
    print(f"   ✓ Correct: {expected_fast_model}")

    # Test 4: Verify tool-calling model actually works
    print("\n4. Testing tool-calling model connection...")
    try:
        response = llm_tools.invoke("Reply with just 'OK'")
        print(f"   ✓ Response: {response.content[:50]}")
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")
        raise

    print("\n" + "=" * 60)
    print("\n✅ Checkpoint 1.2 PASSED - Model routing working!")
    print("\nRouting Summary:")
    print(f"  Tool calling → {config.MODELS['tool_calling']}")
    print(f"  Reasoning    → {config.MODELS['reasoning']}")
    print(f"  Fast queries → {config.MODELS['fast']}")
    return True


if __name__ == "__main__":
    try:
        test_model_routing()
    except Exception as e:
        print(f"\n❌ Checkpoint 1.2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
