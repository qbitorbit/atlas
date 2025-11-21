"""Domain registry for managing available domains."""

from typing import Dict, Optional, List
from .base_domain import BaseDomain


class DomainRegistry:
    """Registry for domain discovery and management."""

    def __init__(self):
        """Initialize domain registry."""
        self._domains: Dict[str, BaseDomain] = {}

    def register(self, domain: BaseDomain):
        """
        Register a domain.

        Args:
            domain: Domain instance to register
        """
        self._domains[domain.name] = domain

    def get(self, name: str) -> Optional[BaseDomain]:
        """
        Get domain by name.

        Args:
            name: Domain name

        Returns:
            BaseDomain or None if not found
        """
        return self._domains.get(name)

    def list_domains(self) -> List[str]:
        """Get list of registered domain names."""
        return list(self._domains.keys())

    def get_all(self) -> Dict[str, BaseDomain]:
        """Get all registered domains."""
        return self._domains.copy()

    def unregister(self, name: str) -> bool:
        """
        Unregister a domain.

        Args:
            name: Domain name to unregister

        Returns:
            bool: True if unregistered, False if not found
        """
        if name in self._domains:
            del self._domains[name]
            return True
        return False


# Global registry instance
_registry = DomainRegistry()


def get_registry() -> DomainRegistry:
    """Get global domain registry instance."""
    return _registry

