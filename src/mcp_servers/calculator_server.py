"""
Calculator MCP Server (calculator-mcp) – port 3005.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator-mcp")


@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Supports +, -, *, /, **, %, and parentheses.
    Example: calculate("150 * 5 + 450")"""
    allowed = set("0123456789+-*/().% ")
    if not all(c in allowed for c in expression):
        return f"Error: expression contains invalid characters. Only numbers and +-*/().% allowed."
    try:
        result = eval(expression)  # noqa: S307 – safe: validated charset
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


@mcp.tool()
def percentage(value: float, percent: float) -> str:
    """Calculate a percentage of a value. E.g. percentage(200, 15) = 15% of 200."""
    result = value * percent / 100
    return f"{percent}% of {value} = {result}"


@mcp.tool()
def split_cost(total: float, people: int) -> str:
    """Split a total cost equally among a number of people."""
    if people <= 0:
        return "Error: number of people must be positive."
    per_person = total / people
    return f"${total:,.2f} split {people} ways = ${per_person:,.2f} per person"


if __name__ == "__main__":
    mcp.run(transport="sse", host="localhost", port=3005)
