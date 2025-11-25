#!/usr/bin/env python3
"""
DeepAgents CLI Wrapper for Open Source Models (v3 - Tool Calling Support)

This wrapper allows you to use the deepagents-cli with your internal
open source models served via OpenAI-compatible API.

IMPORTANT: DeepAgents requires a model that supports TOOL CALLING.
The gpt-oss models do NOT support tool calling, so we use Qwen instead.

Usage:
    python deepagents_oss_v3.py
    python deepagents_oss_v3.py --agent myagent
    python deepagents_oss_v3.py --auto-approve
    python deepagents_oss_v3.py --test  # Test connection first
"""

import os
import sys

# ============================================================================
# PROXY FIXES - Apply before any imports
# ============================================================================

# Clear all proxy settings that might interfere with internal network
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

# Set no_proxy to bypass proxy for internal IPs
os.environ['no_proxy'] = '10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,localhost,127.0.0.1'
os.environ['NO_PROXY'] = os.environ['no_proxy']

# ============================================================================
# MODEL CONFIGURATION - Edit this section to match your setup
# ============================================================================

MODEL_CONFIG = {
    # Your internal LLM server endpoint
    "base_url": "http://10.202.1.3:8000/v1",
    
    # API key (use "dummy-key" if your server doesn't require auth)
    "api_key": "dummy-key",
    
    # IMPORTANT: DeepAgents requires tool calling support!
    # gpt-oss models do NOT support tool calling, use Qwen instead
    "default_model": "/models/Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8",
    
    # Alternative models (for reference)
    "models": {
        # Model that supports tool calling (REQUIRED for deepagents)
        "tool_calling": "/models/Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8",
        # Reasoning model (does NOT support tool calling - don't use with deepagents)
        "reasoning": "/models/openai/gpt-oss-120b",
    },
    
    # LLM parameters
    "temperature": 0.1,
    "max_tokens": 2000,
    "timeout": 60,
}

# ============================================================================
# WRAPPER CODE - No need to edit below this line
# ============================================================================

def patch_create_model():
    """
    Monkey-patch the deepagents_cli.config.create_model function
    to use our internal models instead of cloud APIs.
    """
    from langchain_openai import ChatOpenAI
    from deepagents_cli import config
    
    def create_model_oss():
        """Create model connected to internal OpenAI-compatible API."""
        model_name = os.environ.get("DEEPAGENTS_MODEL", MODEL_CONFIG["default_model"])
        base_url = os.environ.get("DEEPAGENTS_BASE_URL", MODEL_CONFIG["base_url"])
        api_key = os.environ.get("DEEPAGENTS_API_KEY", MODEL_CONFIG["api_key"])
        temperature = float(os.environ.get("DEEPAGENTS_TEMPERATURE", MODEL_CONFIG["temperature"]))
        
        config.console.print(f"[dim]Using OSS model: {model_name}[/dim]")
        config.console.print(f"[dim]Endpoint: {base_url}[/dim]")
        
        # Check if using a model that doesn't support tool calling
        if "gpt-oss" in model_name.lower():
            config.console.print("[yellow]⚠ Warning: gpt-oss models don't support tool calling![/yellow]")
            config.console.print("[yellow]  DeepAgents requires tool calling. Switching to Qwen model.[/yellow]")
            model_name = MODEL_CONFIG["models"]["tool_calling"]
            config.console.print(f"[dim]Switched to: {model_name}[/dim]")
        
        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model=model_name,
            temperature=temperature,
        )
    
    # Replace the original create_model function
    config.create_model = create_model_oss
    
    # Also patch settings to pretend we have an API key
    config.settings.openai_api_key = MODEL_CONFIG["api_key"]


def test_connection():
    """Test the LLM connection before starting the CLI."""
    import httpx
    from langchain_openai import ChatOpenAI
    
    base_url = MODEL_CONFIG["base_url"]
    model_name = MODEL_CONFIG["default_model"]
    
    print(f"Testing connection to {base_url}...")
    print(f"Model: {model_name}")
    print()
    
    try:
        # Test 1: Basic connectivity to /models endpoint
        print("1. Testing /models endpoint...")
        client = httpx.Client(timeout=10.0)
        response = client.get(f"{base_url}/models")
        
        if response.status_code == 200:
            print(f"   ✓ Models endpoint accessible")
        else:
            print(f"   ✗ Got status code: {response.status_code}")
            return False
        
        # Test 2: Actual chat completion
        print("2. Testing chat completion...")
        llm = ChatOpenAI(
            base_url=base_url,
            api_key=MODEL_CONFIG["api_key"],
            model=model_name,
            temperature=MODEL_CONFIG["temperature"],
        )
        
        response = llm.invoke("Say 'hello' and nothing else.")
        print(f"   ✓ Chat completion works!")
        print(f"   Response: {response.content[:100]}...")
        
        # Test 3: Tool calling support
        print("3. Testing tool calling support...")
        from langchain_core.tools import tool
        
        @tool
        def test_tool(query: str) -> str:
            """A test tool that echoes input."""
            return f"Echo: {query}"
        
        llm_with_tools = llm.bind_tools([test_tool])
        response = llm_with_tools.invoke("Use the test_tool to echo 'hello'")
        
        if response.tool_calls:
            print(f"   ✓ Tool calling supported!")
        else:
            print(f"   ⚠ Model responded but didn't use tools")
            print(f"   This might still work, but tool calling may be limited")
        
        print()
        return True
            
    except httpx.ConnectError as e:
        print(f"   ✗ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point - patches the model creation and runs the CLI."""
    
    # Check for --test flag
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        if not test_connection():
            sys.exit(1)
        print("Connection test passed! Starting CLI...\n")
    
    # Set environment variables that LangChain might check
    os.environ.setdefault("OPENAI_API_KEY", MODEL_CONFIG["api_key"])
    os.environ.setdefault("OPENAI_BASE_URL", MODEL_CONFIG["base_url"])
    
    # Apply the monkey patch before importing the CLI main
    patch_create_model()
    
    # Now import and run the CLI
    from deepagents_cli.main import cli_main
    cli_main()


if __name__ == "__main__":
    main()
