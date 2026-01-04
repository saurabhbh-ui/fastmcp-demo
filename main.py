import random
import json
from fastmcp import FastMCP

mcp = FastMCP(name="Simple calculator and randomizer")

@mcp.tool()
def randomization(n_dice: int) -> list[int]:
    "Generate a list of n random integers between 1 and 95."
    return [random.randint(1, 95) for _ in range(n_dice)]

@mcp.tool()
def add_numbers(a: int, b: int) -> str:
    "Addition function for two numbers."
    return f"Final_result :: {a + b}"

@mcp.resource("info://server")
def server_info() -> str:
    info = {
        "name": "Simple Calculator Server",
        "version": "1.0.0",
        "description": "A basic MCP server with math tools",
        "tools": ["add_numbers", "randomization"],
        "author": "Saurabh"
    }
    return json.dumps(info, indent=2)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
