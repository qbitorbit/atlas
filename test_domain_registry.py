"""Test Domain Registry - Checkpoint 2.1"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from domains.registry import DomainRegistry, get_registry
from domains.base_domain import BaseDomain
from llm.router import get_routed_llm
from langchain.tools import tool


def test_domain_registry():
    """Test domain registry system."""
    print("Testing Domain Registry...")
    print("=" * 60)

    # Test 1: Create registry
    print("\n1. Testing registry creation...")
    registry = DomainRegistry()
    print(f"   ✓ Registry created")
    print(f"   Domains count: {len(registry.list_domains())}")

    # Test 2: Register a domain
    print("\n2. Testing domain registration...")

    llm = get_routed_llm(use_tools=True)
    test_domain = BaseDomain(name="test", llm=llm)

    @tool
    def test_tool() -> str:
        """A test tool."""
        return "Test tool executed"

    test_domain.register_tools([test_tool])
    registry.register(test_domain)

    print(f"   ✓ Domain registered: {test_domain.name}")
    print(f"   Domains count: {len(registry.list_domains())}")
    print(f"   Domain tools: {len(test_domain.get_tools())}")

    # Test 3: Retrieve domain
    print("\n3. Testing domain retrieval...")
    retrieved = registry.get("test")
    assert retrieved is not None, "Domain not found"
    assert retrieved.name == "test", f"Wrong domain: {retrieved.name}"
    print(f"   ✓ Retrieved domain: {retrieved.name}")

    # Test 4: List all domains
    print("\n4. Testing domain listing...")
    domains = registry.list_domains()
    print(f"   ✓ Domains: {domains}")
    assert "test" in domains, "Test domain not in list"

    # Test 5: Register multiple domains
    print("\n5. Testing multiple domain registration...")

    android_domain = BaseDomain(name="android", llm=llm)
    database_domain = BaseDomain(name="database", llm=llm)

    registry.register(android_domain)
    registry.register(database_domain)

    print(f"   ✓ Registered: android, database")
    print(f"   Total domains: {len(registry.list_domains())}")
    print(f"   All domains: {registry.list_domains()}")

    # Test 6: Create agent from domain
    print("\n6. Testing domain agent creation...")
    agent = test_domain.create_agent()
    print(f"   ✓ Agent created: {agent.name}")
    print(f"   Agent tools: {len(agent.tools)}")

    # Test 7: Get agent from domain
    print("\n7. Testing domain agent retrieval...")
    retrieved_agent = test_domain.get_agent()
    assert retrieved_agent is not None, "Agent not found"
    print(f"   ✓ Agent retrieved: {retrieved_agent.name}")

    # Test 8: Unregister domain
    print("\n8. Testing domain unregistration...")
    success = registry.unregister("test")
    assert success, "Unregister failed"
    print(f"   ✓ Domain unregistered: test")
    print(f"   Remaining domains: {registry.list_domains()}")

    # Test 9: Global registry
    print("\n9. Testing global registry...")
    global_reg = get_registry()
    print(f"   ✓ Global registry retrieved")

    # Register to global registry
    demo_domain = BaseDomain(name="demo", llm=llm)
    global_reg.register(demo_domain)
    print(f"   ✓ Registered to global: {demo_domain.name}")

    # Retrieve from global
    retrieved_global = get_registry().get("demo")
    assert retrieved_global is not None, "Domain not in global registry"
    print(f"   ✓ Retrieved from global: {retrieved_global.name}")

    print("\n" + "=" * 60)
    print("\n✅ Checkpoint 2.1 PASSED - Domain registry working!")
    print("\nRegistry capabilities:")
    print(f"  ✓ Register and retrieve domains")
    print(f"  ✓ List all registered domains")
    print(f"  ✓ Create agents from domains")
    print(f"  ✓ Global registry singleton pattern")
    print(f"  ✓ Domain unregistration")
    return True


if __name__ == "__main__":
    try:
        test_domain_registry()
    except Exception as e:
        print(f"\n❌ Checkpoint 2.1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
