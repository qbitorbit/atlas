"""LLM configuration settings."""

# LLM server configuration
LLM_BASE_URL = "http://10.202.1.3:8000/v1"
LLM_API_KEY = "dummy-key"

# Model configurations (using correct paths)
MODELS = {
    "tool_calling": "/models/Quen/Qwen3-Coder-480B-A35B-Instruct-FP8",
    "reasoning": "/models/openai/gpt-oss-120b",
    "fast": "/models/openai/gpt-oss-20b"
}

# Default model for agents (must support tool calling)
DEFAULT_MODEL = MODELS["tool_calling"]

# LLM parameters
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 2000
DEFAULT_TIMEOUT = 60
