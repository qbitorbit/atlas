"""LLM configuration settings."""

# LLM server configuration
LLM_BASE_URL = "http://10.202.1.3:8000/v1"
LLM_API_KEY = "dummy-key"

# Model configurations
MODELS = {
    "tool_calling": "/models/openai/Qwen3-Coder-480B-A35B-Instruct-FP8",
    "reasoning": "gpt-oss-120b",
    "fast": "gpt-oss-20b"
}

# Default model for agents (must support tool calling)
DEFAULT_MODEL = MODELS["tool_calling"]

# LLM parameters
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 2000
DEFAULT_TIMEOUT = 60
