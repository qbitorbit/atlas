"""Base agent class for domain-specific agents."""

from typing import List, Optional
from langchain.agents import create_agent
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI


class BaseAgent:
    """Base agent class with tool calling capability."""

    def __init__(
        self,
        llm: ChatOpenAI,
        tools: Optional[List[BaseTool]] = None,
        name: str = "BaseAgent"
    ):
        """
        Initialize base agent.

        Args:
            llm: LLM client instance
            tools: List of tools available to agent
            name: Agent name for identification
        """
        self.llm = llm
        self.tools = tools or []
        self.name = name
        self.agent = None

        if self.tools:
            self._create_agent()

    def _create_agent(self):
        """Create LangChain agent with tools."""
        self.agent = create_agent(model=self.llm, tools=self.tools)

    def add_tool(self, tool: BaseTool):
        """Add a tool to the agent."""
        self.tools.append(tool)
        self._create_agent()

    def invoke(self, query: str) -> dict:
        """
        Execute query using agent or direct LLM.

        Args:
            query: User query string

        Returns:
            dict: Agent response with messages
        """
        if self.agent:
            return self.agent.invoke(
                {"messages": [{"role": "user", "content": query}]}
            )
        else:
            # No tools, use LLM directly
            response = self.llm.invoke(query)
            return {"messages": [{"role": "assistant", "content": response.content}]}
