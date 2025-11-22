"""Supervisor agent for routing queries to domain agents."""

from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from domains.registry import DomainRegistry
from .base_agent import BaseAgent


class SupervisorAgent:
    """Supervisor agent that routes queries to appropriate domain agents."""

    def __init__(self, llm: ChatOpenAI, registry: DomainRegistry):
        """
        Initialize supervisor agent.

        Args:
            llm: LLM client for routing decisions
            registry: Domain registry for accessing domain agents
        """
        self.llm = llm
        self.registry = registry
        self.context: Dict[str, Any] = {}

    def route_query(self, query: str) -> Optional[str]:
        """
        Analyze query and route to appropriate domain using registered keywords.

        Args:
            query: User query

        Returns:
            str: Domain name to route to, or None if no match found
        """
        query_lower = query.lower()
        matched_domains = []

        # Check all registered domains' keywords
        for domain_name, domain_obj in self.registry.get_all().items():
            if any(keyword.lower() in query_lower for keyword in domain_obj.keywords):
                matched_domains.append(domain_name)

        # Return None if no match (let caller handle)
        if not matched_domains:
            return None

        # Return first match (or could handle multiple matches differently)
        return matched_domains[0]

    def invoke(self, query: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Process query with appropriate domain agent.

        Args:
            query: User query
            domain: Specific domain to use (auto-detect if None)

        Returns:
            Dict: Response with domain and result
        """
        # Determine domain
        if not domain:
            domain = self.route_query(query)
            if not domain:
                available_domains = list(self.registry.get_all().keys())
                return {
                    "domain": None,
                    "error": f"Could not determine domain for query. Available domains: {', '.join(available_domains)}",
                    "result": None
                }

        # Get domain from registry
        domain_obj = self.registry.get(domain)
        if not domain_obj:
            return {
                "domain": domain,
                "error": f"Domain not found: {domain}",
                "result": None
            }

        # Get or create domain agent
        agent = domain_obj.get_agent()
        if not agent:
            return {
                "domain": domain,
                "error": f"Failed to create agent for domain: {domain}",
                "result": None
            }

        # Execute query with domain agent
        try:
            result = agent.invoke(query)
            return {
                "domain": domain,
                "error": None,
                "result": result
            }
        except Exception as e:
            return {
                "domain": domain,
                "error": str(e),
                "result": None
            }

    def set_context(self, key: str, value: Any):
        """Set context variable."""
        self.context[key] = value

    def get_context(self, key: str) -> Optional[Any]:
        """Get context variable."""
        return self.context.get(key)

    def clear_context(self):
        """Clear all context."""
        self.context.clear()
