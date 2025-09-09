import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage  # <-- add this

load_dotenv()
llm = ChatOpenAI()


async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": "python",
                "args": [
                    "-u",
                    "/Users/tripti/Documents/GithubProjects/mcp-servers/mcp-crash-course/servers/math_server.py",
                ],
            },
            "weather": {
                "transport": "sse",
                "url": "http://127.0.0.1:8000/sse",
            },
        }
    )

    tools = await client.get_tools()
    # Optional: sanity check
    print("Loaded tools:", [t.name for t in tools])

    agent = create_react_agent(llm, tools)

    # out = await agent.ainvoke(
    #     {"messages": [HumanMessage(content="what is 2 + 2?")]},
    #     config={"recursion_limit": 50},  # <-- bump limit
    # )
    out = await agent.ainvoke(
        {"messages": [HumanMessage(content="what is weather in New York?")]},
        config={"recursion_limit": 50},  # <-- bump limit
    )
    print(out["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
