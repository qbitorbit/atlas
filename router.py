"""Model routing middleware - selects appropriate model based on task."""

from typing import Optional, List
from langchain_openai import ChatOpenAI
from . import config


def get_routed_llm(
    use_tools: bool = False,
    temperature: Optional[float] = None
) -> ChatOpenAI:
    """
    Get LLM client with automatic model routing.

    Args:
        use_tools: If True, uses tool-calling model (Qwen), else reasoning model
        temperature: Temperature for response generation

    Returns:
        ChatOpenAI: Configured LLM client with appropriate model
    """
    if use_tools:
        # Tool calling requires Qwen model
        model = config.MODELS["tool_calling"]
    else:
        # Simple reasoning can use faster model
        model = config.MODELS["reasoning"]

    return ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=model,
        temperature=temperature or config.DEFAULT_TEMPERATURE
    )


def get_fast_llm(temperature: Optional[float] = None) -> ChatOpenAI:
    """
    Get fast LLM for quick queries.

    Returns:
        ChatOpenAI: Fast LLM client
    """
    return ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=config.MODELS["fast"],
        temperature=temperature or config.DEFAULT_TEMPERATURE
    )
