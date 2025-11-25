#!/usr/bin/env python3
"""
DeepAgents CLI Wrapper for Open Source Models

This wrapper allows you to use the deepagents-cli with your internal
open source models served via OpenAI-compatible API (vLLM, etc.)

Usage:
    python deepagents_oss.py
    python deepagents_oss.py --agent myagent
    python deepagents_oss.py --auto-approve

Configuration:
    Edit the MODEL_CONFIG section below to match your internal setup.
"""

import os
import sys

# ============================================================================
# MODEL CONFIGURATION - Edit this section to match your setup
# ============================================================================

MODEL_CONFIG = {
    # Your internal LLM server endpoint
    "base_url": "http://10.202.1.3:8000/v1",
    
    # API key (use "dummy-key" if your server doesn't require auth)
    "api_key": "dummy-key",
    
    # Default model for general reasoning tasks
    "default_model": "/models/openai/gpt-oss-120b",
    
    # Temperature setting (lower = more deterministic)
    "temperature": 0.1,
    
    # Optional: Define additional models for specific tasks
    # These can be used with subagents if you extend the setup
    "models": {
        "reasoning": "/models/openai/gpt-oss-120b",
        "coding": "/models/qwen/qwen-coder",      # Update with your actual path
        "multimodal": "/models/qwen/qwen-vl",     # Update with your actual path
    }
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
        
        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            model=model_name,
            temperature=temperature,
        )
    
    # Replace the original create_model function
    config.create_model = create_model_oss
    
    # Also patch settings to pretend we have an API key
    # This prevents the CLI from complaining about missing keys
    config.settings.openai_api_key = MODEL_CONFIG["api_key"]


def main():
    """Main entry point - patches the model creation and runs the CLI."""
    
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
