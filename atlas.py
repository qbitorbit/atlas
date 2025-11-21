# atlas_test.py - Stream version to debug

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

llm = ChatOpenAI(
    base_url="http://10.202.1.3:8000/v1",
    api_key="dummy-key",
    model="/models/openai/Qwen3-Coder-480B-A35B-Instruct-FP8",
    temperature=0.1
)

@tool
def get_device_info(device_id: str) -> str:
    """Get information about an Android device including battery level.
    
    Args:
        device_id: The device serial number
    """
    print(f"\n🔧 TOOL CALLED: get_device_info(device_id='{device_id}')")
    return f"Device {device_id}: Samsung Galaxy S24+, Android 14, Battery: 85%"

agent = create_agent(model=llm, tools=[get_device_info])

print("🧪 Testing Atlas - Basic Agent + Tools + LLM\n")
print("=" * 60)

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "What is the battery level of device ABC123?"}]},
    stream_mode="values"
):
    latest_msg = chunk["messages"][-1]
    print(f"\n📨 Message type: {latest_msg.type}")
    if hasattr(latest_msg, 'content') and latest_msg.content:
        print(f"Content: {latest_msg.content}")
    if hasattr(latest_msg, 'tool_calls') and latest_msg.tool_calls:
        print(f"Tool calls: {latest_msg.tool_calls}")

print("\n" + "=" * 60)
print("\n✅ Atlas basic infrastructure works!")
