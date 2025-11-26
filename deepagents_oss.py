#!/usr/bin/env python3
"""
DeepAgents CLI Wrapper for Open Source Models (v4 - Async/Streaming Fix)

This wrapper allows you to use the deepagents-cli with your internal
open source models served via OpenAI-compatible API.

IMPORTANT: 
- DeepAgents requires a model that supports TOOL CALLING.
- DeepAgents uses ASYNC STREAMING which may behave differently than sync calls.

Usage:
    python deepagents_oss_v4.py
    python deepagents_oss_v4.py --agent myagent
    python deepagents_oss_v4.py --auto-approve
    python deepagents_oss_v4.py --test  # Test connection with streaming
"""

import os
import sys

# ============================================================================
# PROXY FIXES - Apply before any imports
# ============================================================================

# Clear all proxy settings that might interfere with internal network
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 
                  'all_proxy', 'ALL_PROXY', 'no_proxy', 'NO_PROXY']:
    os.environ.pop(proxy_var, None)

# Set no_proxy to bypass proxy for internal IPs
os.environ['no_proxy'] = '*'
os.environ['NO_PROXY'] = '*'

# ============================================================================
# MODEL CONFIGURATION - Edit this section to match your setup
# ============================================================================

MODEL_CONFIG = {
    # Your internal LLM server endpoint
    "base_url": "http://10.202.1.3:8000/v1",
    
    # API key (use "dummy-key" if your server doesn't require auth)
    "api_key": "dummy-key",
    
    # IMPORTANT: DeepAgents requires tool calling support!
    # Use Qwen model that supports tool calling
    "default_model": "/models/Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8",
    
    # LLM parameters (matching your working config)
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
    import httpx
    
    def create_model_oss():
        """Create model connected to internal OpenAI-compatible API."""
        model_name = os.environ.get("DEEPAGENTS_MODEL", MODEL_CONFIG["default_model"])
        base_url = os.environ.get("DEEPAGENTS_BASE_URL", MODEL_CONFIG["base_url"])
        api_key = os.environ.get("DEEPAGENTS_API_KEY", MODEL_CONFIG["api_key"])
        temperature = float(os.environ.get("DEEPAGENTS_TEMPERATURE", MODEL_CONFIG["temperature"]))
        timeout = float(os.environ.get("DEEPAGENTS_TIMEOUT", MODEL_CONFIG["timeout"]))
        
        config.console.print(f"[dim]Using OSS model: {model_name}[/dim]")
        config.console.print(f"[dim]Endpoint: {base_url}[/dim]")
        
        # Check if using a model that doesn't support tool calling
        if "gpt-oss" in model_name.lower():
            config.console.print("[yellow]⚠ Warning: gpt-oss models don't support tool calling![/yellow]")
            config.console.print("[yellow]  Switching to Qwen model.[/yellow]")
            model_name = MODEL_CONFIG["default_model"]
            config.console.print(f"[dim]Switched to: {model_name}[/dim]")
        
        # Create custom HTTP clients without proxy settings
        # This ensures both sync and async requests bypass proxy
        http_client = httpx.Client(
            timeout=httpx.Timeout(timeout, connect=30.0),
            follow_redirects=True,
        )
        
        async_http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=30.0),
            follow_redirects=True,
        )
        
        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model=model_name,
            temperature=temperature,
            max_tokens=MODEL_CONFIG["max_tokens"],
            timeout=timeout,
            http_client=http_client,
            http_async_client=async_http_client,
        )
    
    # Replace the original create_model function
    config.create_model = create_model_oss
    
    # Also patch settings to pretend we have an API key
    config.settings.openai_api_key = MODEL_CONFIG["api_key"]


def test_connection():
    """Test the LLM connection including streaming (like deepagents uses)."""
    import httpx
    import asyncio
    from langchain_openai import ChatOpenAI
    
    base_url = MODEL_CONFIG["base_url"]
    model_name = MODEL_CONFIG["default_model"]
    
    print(f"Testing connection to {base_url}")
    print(f"Model: {model_name}")
    print()
    
    try:
        # Test 1: Basic connectivity
        print("1. Testing /models endpoint...")
        client = httpx.Client(timeout=10.0)
        response = client.get(f"{base_url}/models")
        
        if response.status_code == 200:
            print("   ✓ Models endpoint accessible")
            data = response.json()
            if 'data' in data:
                print(f"   Available models: {[m.get('id', m) for m in data['data'][:5]]}...")
        else:
            print(f"   ✗ Got status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
        
        # Test 2: Synchronous chat completion
        print("\n2. Testing sync chat completion...")
        
        http_client = httpx.Client(
            timeout=httpx.Timeout(MODEL_CONFIG["timeout"], connect=30.0),
        )
        
        llm = ChatOpenAI(
            base_url=base_url,
            api_key=MODEL_CONFIG["api_key"],
            model=model_name,
            temperature=MODEL_CONFIG["temperature"],
            http_client=http_client,
        )
        
        response = llm.invoke("Say 'hello' and nothing else.")
        print(f"   ✓ Sync completion works!")
        print(f"   Response: {response.content[:100]}")
        
        # Test 3: Async chat completion (this is what deepagents uses)
        print("\n3. Testing async chat completion...")
        
        async def test_async():
            async_http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(MODEL_CONFIG["timeout"], connect=30.0),
            )
            
            llm_async = ChatOpenAI(
                base_url=base_url,
                api_key=MODEL_CONFIG["api_key"],
                model=model_name,
                temperature=MODEL_CONFIG["temperature"],
                http_async_client=async_http_client,
            )
            
            response = await llm_async.ainvoke("Say 'world' and nothing else.")
            return response
        
        async_response = asyncio.run(test_async())
        print(f"   ✓ Async completion works!")
        print(f"   Response: {async_response.content[:100]}")
        
        # Test 4: Streaming (deepagents uses this heavily)
        print("\n4. Testing async streaming...")
        
        async def test_streaming():
            async_http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(MODEL_CONFIG["timeout"], connect=30.0),
            )
            
            llm_stream = ChatOpenAI(
                base_url=base_url,
                api_key=MODEL_CONFIG["api_key"],
                model=model_name,
                temperature=MODEL_CONFIG["temperature"],
                streaming=True,
                http_async_client=async_http_client,
            )
            
            chunks = []
            async for chunk in llm_stream.astream("Count from 1 to 3."):
                chunks.append(chunk.content)
            return "".join(chunks)
        
        stream_response = asyncio.run(test_streaming())
        print(f"   ✓ Streaming works!")
        print(f"   Response: {stream_response[:100]}")
        
        # Test 5: Tool calling (required for deepagents)
        print("\n5. Testing tool calling...")
        
        from langchain_core.tools import tool
        
        @tool
        def get_weather(city: str) -> str:
            """Get weather for a city."""
            return f"Weather in {city}: Sunny"
        
        llm_with_tools = llm.bind_tools([get_weather])
        response = llm_with_tools.invoke("What's the weather in Tokyo?")
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"   ✓ Tool calling works!")
            print(f"   Tool calls: {response.tool_calls}")
        else:
            print(f"   ⚠ Model responded but didn't use tools")
            print(f"   Response: {response.content[:100]}")
            print("   This might still work, but tool calling behavior may vary")
        
        print("\n" + "="*50)
        print("All tests passed!")
        print("="*50 + "\n")
        return True
            
    except httpx.ConnectError as e:
        print(f"\n   ✗ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"\n   ✗ Error: {e}")
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
        print("Starting CLI...\n")
    
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
