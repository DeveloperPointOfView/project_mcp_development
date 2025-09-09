# STDIO MCP server exposing a simple math tool
from fastmcp import FastMCP

mcp = FastMCP("math-server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b


@mcp.tool()
def mul(a: float, b: float) -> float:
    """Multiply two numbers and return the product."""
    return a * b


if __name__ == "__main__":
    # IMPORTANT: This runs a pure STDIO server (no HTTP, no Uvicorn)
    mcp.run()
