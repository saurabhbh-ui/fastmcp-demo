import random 
from fastmcp import FastMCP

mcp = FastMCP(name="Demo")

@mcp.tool
def randomization(n_dice) -> list[int]:
    "Generate a list of n random integers between 1 and 95."
    return [random.randint(1, 95) for _ in range(n_dice)]

@mcp.tool
def add_numbers(a: int, b: int) -> str:
    "Addition function for two numbers."

    return f"Final_result :: {a + b}"


if __name__ == "__main__":
    mcp.run()










