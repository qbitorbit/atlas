#!/usr/bin/env python3
"""
DeepAgents CLI Wrapper for Open Source Models (v2 - with proxy fixes)

This wrapper allows you to use the deepagents-cli with your internal
open source models served via OpenAI-compatible API (vLLM, etc.)

Usage:
    python deepagents_oss_v2.py
    python deepagents_oss_v2.py --agent myagent
    python deepagents_oss_v2.py --auto-approve

Configuration:
    Edit the MODEL_CONFIG section below to match your internal setup.
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
    # Your internal LLM server endpoint (make sure it ends with /v1)
    "base_url": "http://10.202.1.3:8000/v1",
    
    # API key (use "dummy-key" if your server doesn't require auth)
    "api_key": "dummy-key",
    
    # Default model - adjust the path format if needed
    # Try these formats if one doesn't work:
    #   "/models/openai/gpt-oss-120b"
    #   "openai/gpt-oss-120b"  
    #   "gpt-oss-120b"
    "default_model": "/models/openai/gpt-oss-120b",
    
    # Temperature setting (lower = more deterministic)
    "temperature": 0.1,
    
    # Request timeout in seconds (increase if your model is slow)
    "timeout": 120,
    
    # Max retries on failure
    "max_retries": 2,
}

# ============================================================================
# WRAPPER CODE - No need to edit below this line
# ============================================================================

def patch_create_model():
    """
    Monkey-patch the deepagents_cli.config.create_model function
    to use our internal models instead of cloud APIs.
    """
    import httpx
    from langchain_openai import ChatOpenAI
    from deepagents_cli import config
    
    def create_model_oss():
        """Create model connected to internal OpenAI-compatible API."""
        model_name = os.environ.get("DEEPAGENTS_MODEL", MODEL_CONFIG["default_model"])
        base_url = os.environ.get("DEEPAGENTS_BASE_URL", MODEL_CONFIG["base_url"])
        api_key = os.environ.get("DEEPAGENTS_API_KEY", MODEL_CONFIG["api_key"])
        temperature = float(os.environ.get("DEEPAGENTS_TEMPERATURE", MODEL_CONFIG["temperature"]))
        timeout = float(os.environ.get("DEEPAGENTS_TIMEOUT", MODEL_CONFIG["timeout"]))
        max_retries = int(os.environ.get("DEEPAGENTS_MAX_RETRIES", MODEL_CONFIG["max_retries"]))
        
        config.console.print(f"[dim]Using OSS model: {model_name}[/dim]")
        config.console.print(f"[dim]Endpoint: {base_url}[/dim]")
        
        # Create httpx client without proxy
        http_client = httpx.Client(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )
        
        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model=model_name,
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
    
    # Replace the original create_model function
    config.create_model = create_model_oss
    
    # Also patch settings to pretend we have an API key
    config.settings.openai_api_key = MODEL_CONFIG["api_key"]


def test_connection():
    """Test the LLM connection before starting the CLI."""
    import httpx
    
    base_url = MODEL_CONFIG["base_url"]
    
    print(f"Testing connection to {base_url}...")
    
    try:
        # Test basic connectivity
        client = httpx.Client(timeout=10.0)
        
        # Try to hit the models endpoint
        response = client.get(f"{base_url}/models")
        
        if response.status_code == 200:
            print(f"✓ Connection successful!")
            models = response.json()
            print(f"✓ Available models: {models}")
            return True
        else:
            print(f"✗ Got status code: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False
            
    except httpx.ConnectError as e:
        print(f"✗ Connection failed: {e}")
        print("  Check if the server is running and accessible")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main entry point - patches the model creation and runs the CLI."""
    
    # Check for --test flag
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        if not test_connection():
            sys.exit(1)
        print("\nConnection test passed! Starting CLI...\n")
    
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
