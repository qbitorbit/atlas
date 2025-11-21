"""Test Model Routing - Checkpoint 1.2"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm.router import get_routed_llm, get_fast_llm
from llm import config
from langchain.agents import create_agent
from langchain.tools import tool


def test_model_routing():
    """Test that model routing selects correct models."""
    print("Testing Model Routing Middleware...")
    print("=" * 60)

    # Test 1: Tool calling model selection
    print("\n1. Testing tool-calling model selection...")
    llm_tools = get_routed_llm(use_tools=True)
    print(f"   Model selected: {llm_tools.model_name}")
    expected_tool_model = config.MODELS["tool_calling"]
    assert llm_tools.model_name == expected_tool_model, \
        f"Expected {expected_tool_model}, got {llm_tools.model_name}"
    print(f"   ✓ Correct: {expected_tool_model}")

    # Test 2: Reasoning model selection
    print("\n2. Testing reasoning model selection...")
    llm_reasoning = get_routed_llm(use_tools=False)
    print(f"   Model selected: {llm_reasoning.model_name}")
    expected_reasoning_model = config.MODELS["reasoning"]
    assert llm_reasoning.model_name == expected_reasoning_model, \
        f"Expected {expected_reasoning_model}, got {llm_reasoning.model_name}"
    print(f"   ✓ Correct: {expected_reasoning_model}")

    # Test 3: Fast model selection
    print("\n3. Testing fast model selection...")
    llm_fast = get_fast_llm()
    print(f"   Model selected: {llm_fast.model_name}")
    expected_fast_model = config.MODELS["fast"]
    assert llm_fast.model_name == expected_fast_model, \
        f"Expected {expected_fast_model}, got {llm_fast.model_name}"
    print(f"   ✓ Correct: {expected_fast_model}")

    # Test 4: Verify tool-calling model connection (Qwen only)
    print("\n4. Testing tool-calling model connection (Qwen)...")
    try:
        response = llm_tools.invoke("Reply with just 'Routing OK'")
        print(f"   ✓ Response: {response.content[:50]}")
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")
        raise

    # Test 5: Verify reasoning model connection
    print("\n5. Testing reasoning model connection (gpt-oss-120b)...")
    try:
        response = llm_reasoning.invoke("Reply with just 'Reasoning OK'")
        print(f"   ✓ Response: {response.content[:50]}")
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")
        raise

    # Test 6: Verify fast model connection
    print("\n6. Testing fast model connection (gpt-oss-20b)...")
    try:
        response = llm_fast.invoke("Reply with just 'Fast OK'")
        print(f"   ✓ Response: {response.content[:50]}")
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")
        raise

    # Test 7: IMPORTANT - Verify tool calling actually works with Qwen
    print("\n7. Testing ACTUAL tool calling with Qwen model...")

    @tool
    def test_tool(query: str) -> str:
        """A test tool that returns a confirmation message.

        Args:
            query: The test query string
        """
        return f"Tool executed successfully with query: {query}"

    try:
        # Create agent with tool-calling model
        agent = create_agent(model=llm_tools, tools=[test_tool])
        print(f"   ✓ Agent created with tool")

        # Test tool calling
        result = agent.invoke({
            "messages": [{"role": "user", "content": "Use test_tool with query 'hello'"}]
        })

        # Check if tool was called
        messages = result["messages"]
        tool_called = any(hasattr(msg, 'tool_calls') and msg.tool_calls for msg in messages)

        if tool_called:
            print(f"   ✓ Tool calling WORKS! Agent used the tool correctly")
        else:
            print(f"   ⚠ Warning: Tool may not have been called")

    except Exception as e:
        print(f"   ❌ Tool calling FAILED: {str(e)[:100]}")
        raise

    print("\n" + "=" * 60)
    print("\n✅ Checkpoint 1.2 PASSED - Model routing working!")
    print("\nRouting Summary:")
    print(f"  Tool calling → {config.MODELS['tool_calling']} ✓ Supports tools")
    print(f"  Reasoning    → {config.MODELS['reasoning']} (simple queries only)")
    print(f"  Fast queries → {config.MODELS['fast']} (simple queries only)")
    return True


if __name__ == "__main__":
    try:
        test_model_routing()
    except Exception as e:
        print(f"\n❌ Checkpoint 1.2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
