"""LLM client for connecting to on-premise LLM server."""

from langchain_openai import ChatOpenAI
from typing import Optional
from . import config


def get_llm_client(
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> ChatOpenAI:
    """
    Create and return LLM client instance.

    Args:
        model: Model name to use (defaults to tool_calling model)
        temperature: Temperature for response generation

    Returns:
        ChatOpenAI: Configured LLM client
    """
    return ChatOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        model=model or config.DEFAULT_MODEL,
        temperature=temperature or config.DEFAULT_TEMPERATURE
    )
