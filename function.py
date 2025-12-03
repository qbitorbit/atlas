def create_model(model_name: Optional[str] = None) -> BaseChatModel:
    """Create LLM model - MODIFIED for internal vLLM server."""
    
    # INTERNAL vLLM CONFIGURATION
    from langchain_openai import ChatOpenAI
    
    LLM_BASE_URL = "http://10.202.1.3:8000/v1"
    LLM_API_KEY = "dummy-key"
    
    # Use Qwen Coder (supports tools - required by deepagents)
    DEFAULT_MODEL = "/models/Qwen/Qwen3-Coder-30BB-A3B-Instruct"
    
    print(f"[INTERNAL] Using model: {DEFAULT_MODEL}")
    print(f"[INTERNAL] Server: {LLM_BASE_URL}")
    
    return ChatOpenAI(
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        model=model_name or DEFAULT_MODEL,
        temperature=0.1
    )
