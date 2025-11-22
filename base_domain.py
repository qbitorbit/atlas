# """Base domain class for domain-specific implementations."""

# from typing import List, Optional
# from langchain.tools import BaseTool
# from agents.base_agent import BaseAgent
# from langchain_openai import ChatOpenAI


# class BaseDomain:
#     """Base class for all domain implementations."""

#     def __init__(self, name: str, llm: ChatOpenAI):
#         """
#         Initialize domain.

#         Args:
#             name: Domain name
#             llm: LLM client for agent
#         """
#         self.name = name
#         self.llm = llm
#         self.tools: List[BaseTool] = []
#         self.agent: Optional[BaseAgent] = None

#     def register_tools(self, tools: List[BaseTool]):
#         """Register tools for this domain."""
#         self.tools.extend(tools)

#     def get_tools(self) -> List[BaseTool]:
#         """Get all registered tools."""
#         return self.tools

#     def create_agent(self) -> BaseAgent:
#         """Create domain agent with registered tools."""
#         self.agent = BaseAgent(
#             llm=self.llm,
#             tools=self.tools,
#             name=f"{self.name}Agent"
#         )
#         return self.agent

#     def get_agent(self) -> Optional[BaseAgent]:
#         """Get domain agent (create if not exists)."""
#         if not self.agent:
#             self.create_agent()
#         return self.agent


"""Base domain class for domain-specific implementations."""

from typing import List, Optional
from langchain.tools import BaseTool
from agents.base_agent import BaseAgent
from langchain_openai import ChatOpenAI


class BaseDomain:
    """Base class for all domain implementations."""

    def __init__(self, name: str, llm: ChatOpenAI, keywords: Optional[List[str]] = None):
        """
        Initialize domain.

        Args:
            name: Domain name
            llm: LLM client for agent
            keywords: Keywords for routing queries to this domain
        """
        self.name = name
        self.llm = llm
        self.keywords = keywords or []
        self.tools: List[BaseTool] = []
        self.agent: Optional[BaseAgent] = None

    def register_tools(self, tools: List[BaseTool]):
        """Register tools for this domain."""
        self.tools.extend(tools)

    def get_tools(self) -> List[BaseTool]:
        """Get all registered tools."""
        return self.tools

    def create_agent(self) -> BaseAgent:
        """Create domain agent with registered tools."""
        self.agent = BaseAgent(
            llm=self.llm,
            tools=self.tools,
            name=f"{self.name}Agent"
        )
        return self.agent

    def get_agent(self) -> Optional[BaseAgent]:
        """Get domain agent (create if not exists)."""
        if not self.agent:
            self.create_agent()
        return self.agent

