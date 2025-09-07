import asyncio
import os
import sys
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

load_dotenv()

# Initialize LLM (expects OPENAI_API_KEY in env)
llm = ChatOpenAI()

# Use the current interpreter to run the MCP server in the same venv
stdio_server_params = StdioServerParameters(
    command=sys.executable,  # or "python3"
    args=[
        "/Users/tripti/Documents/GithubProjects/mcp-servers/mcp-crash-course/servers/math_server.py"
    ],
    env=os.environ.copy(),
)

async def main():
    async with stdio_client(stdio_server_params) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
            await session.initialize()
            print("✅ Connected to the MCP server.")

            # Load MCP tools from the session
            mcp_tools = await load_mcp_tools(session)
            print(f"🔧 Loaded {len(mcp_tools)} tool(s): {[t.name for t in mcp_tools]}")

            # (Optional) Build an agent that can use those tools
            agent = create_react_agent(llm, tools=mcp_tools)

            # Quick smoke test: show the agent’s available tools
            # (In real use, you'd call agent with a task prompt.)
            for t in mcp_tools:
                print(f"- {t.name}: {t.description}")

            # Example (uncomment to run a single call):
            result = await agent.ainvoke({"messages": [HumanMessage(content="what is 55*68*56+4567?")]})
            print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())