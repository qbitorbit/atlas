"""Test Supervisor Agent - Checkpoint 3.1"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.supervisor import SupervisorAgent
from domains.registry import DomainRegistry
from domains.base_domain import BaseDomain
from llm.router import get_routed_llm
from langchain.tools import tool


def test_supervisor():
    """Test supervisor agent routing."""
    print("Testing Supervisor Agent...")
    print("=" * 60)

    # Test 1: Create supervisor
    print("\n1. Creating supervisor agent...")
    llm = get_routed_llm(use_tools=True)
    registry = DomainRegistry()
    supervisor = SupervisorAgent(llm=llm, registry=registry)
    print(f"   ✓ Supervisor created")

    # Test 2: Register test domains with keywords
    print("\n2. Registering test domains with keywords...")

    # Android domain with keywords
    @tool
    def test_android_tool() -> str:
        """Test Android tool."""
        return "Android tool executed"

    android_keywords = ["device", "phone", "android", "app", "install", "screenshot", "tap", "logcat", "adb", "apk"]
    android_domain = BaseDomain(name="android", llm=llm, keywords=android_keywords)
    android_domain.register_tools([test_android_tool])
    registry.register(android_domain)
    print(f"   ✓ Registered: android (keywords: {len(android_keywords)})")

    # Database domain with keywords
    @tool
    def test_database_tool() -> str:
        """Test Database tool."""
        return "Database tool executed"

    database_keywords = ["database", "sql", "query", "table", "select", "insert", "schema"]
    database_domain = BaseDomain(name="database", llm=llm, keywords=database_keywords)
    database_domain.register_tools([test_database_tool])
    registry.register(database_domain)
    print(f"   ✓ Registered: database (keywords: {len(database_keywords)})")

    # Kubernetes domain with keywords
    @tool
    def test_kubernetes_tool() -> str:
        """Test Kubernetes tool."""
        return "Kubernetes tool executed"

    k8s_keywords = ["kubernetes", "k8s", "pod", "deployment", "service", "namespace", "cluster", "kubectl"]
    k8s_domain = BaseDomain(name="kubernetes", llm=llm, keywords=k8s_keywords)
    k8s_domain.register_tools([test_kubernetes_tool])
    registry.register(k8s_domain)
    print(f"   ✓ Registered: kubernetes (keywords: {len(k8s_keywords)})")

    print(f"   Total domains: {len(registry.list_domains())}")

    # Test 3: Query routing - Android
    print("\n3. Testing Android domain routing...")
    android_query = "List all devices"
    routed_domain = supervisor.route_query(android_query)
    print(f"   Query: '{android_query}'")
    print(f"   Routed to: {routed_domain}")
    assert routed_domain == "android", f"Expected 'android', got '{routed_domain}'"
    print(f"   ✓ Correct routing")

    # Test 4: Query routing - Database
    print("\n4. Testing Database domain routing...")
    db_query = "Show me all tables in the database"
    routed_domain = supervisor.route_query(db_query)
    print(f"   Query: '{db_query}'")
    print(f"   Routed to: {routed_domain}")
    assert routed_domain == "database", f"Expected 'database', got '{routed_domain}'"
    print(f"   ✓ Correct routing")

    # Test 4b: Query routing - Kubernetes
    print("\n4b. Testing Kubernetes domain routing...")
    k8s_query = "List all pods in the cluster"
    routed_domain = supervisor.route_query(k8s_query)
    print(f"   Query: '{k8s_query}'")
    print(f"   Routed to: {routed_domain}")
    assert routed_domain == "kubernetes", f"Expected 'kubernetes', got '{routed_domain}'"
    print(f"   ✓ Correct routing")

    # Test 5: Execute query via supervisor
    print("\n5. Testing query execution...")
    result = supervisor.invoke("test android")
    print(f"   Domain: {result['domain']}")
    print(f"   Error: {result['error']}")
    print(f"   Result type: {type(result['result'])}")
    assert result['domain'] == 'android', "Should route to android"
    assert result['error'] is None, f"Should have no error: {result['error']}"
    print(f"   ✓ Query executed successfully")

    # Test 6: Context management
    print("\n6. Testing context management...")
    supervisor.set_context("device_id", "emulator-5554")
    device_id = supervisor.get_context("device_id")
    print(f"   Set context: device_id = {device_id}")
    assert device_id == "emulator-5554", "Context not set correctly"
    print(f"   ✓ Context management working")

    supervisor.clear_context()
    device_id = supervisor.get_context("device_id")
    assert device_id is None, "Context not cleared"
    print(f"   ✓ Context cleared")

    # Test 7: Unknown query handling (no keyword match)
    print("\n7. Testing unknown query handling...")
    result = supervisor.invoke("what is the weather today")
    print(f"   Query: 'what is the weather today'")
    print(f"   Domain: {result['domain']}")
    print(f"   Error: {result['error'][:80] if result['error'] else None}")
    assert result['domain'] is None, "Should be None for unknown query"
    assert result['error'] is not None, "Should have error for unknown query"
    print(f"   ✓ Unknown query handled correctly (no default domain)")

    # Test 8: Invalid domain name
    print("\n8. Testing invalid domain handling...")
    result = supervisor.invoke("test query", domain="nonexistent")
    print(f"   Domain: {result['domain']}")
    print(f"   Error: {result['error']}")
    assert result['error'] is not None, "Should have error for invalid domain"
    print(f"   ✓ Invalid domain handled correctly")

    print("\n" + "=" * 60)
    print("\n✅ Checkpoint 3.1 PASSED - Supervisor agent working!")
    print("\nSupervisor capabilities:")
    print(f"  ✓ Dynamic domain routing (keyword-based)")
    print(f"  ✓ No hardcoded keywords - domains register their own")
    print(f"  ✓ Support for Android, Database, Kubernetes domains")
    print(f"  ✓ Unknown query handling (no default domain)")
    print(f"  ✓ Domain agent execution")
    print(f"  ✓ Context management")
    print(f"  ✓ Error handling")
    print("\nEasy to extend:")
    print(f"  - Just create new domain with keywords")
    print(f"  - Register it - no code changes needed!")
    return True


if __name__ == "__main__":
    try:
        test_supervisor()
    except Exception as e:
        print(f"\n❌ Checkpoint 3.1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
