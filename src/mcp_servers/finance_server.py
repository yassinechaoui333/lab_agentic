"""
Finance MCP Server (finance-mcp)
Estimates total travel cost based on destination and number of days.
Runs on port 3002.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("finance-mcp")

# --------------------------------------------------------------------------- #
#  Cost profiles per destination (daily averages in USD)
# --------------------------------------------------------------------------- #
COST_PROFILES: dict[str, dict[str, float]] = {
    "barcelona": {
        "accommodation": 120.0,
        "food": 55.0,
        "transport": 15.0,
        "activities": 40.0,
        "miscellaneous": 20.0,
    },
    "paris": {
        "accommodation": 160.0,
        "food": 65.0,
        "transport": 18.0,
        "activities": 50.0,
        "miscellaneous": 25.0,
    },
    "tokyo": {
        "accommodation": 140.0,
        "food": 50.0,
        "transport": 20.0,
        "activities": 45.0,
        "miscellaneous": 22.0,
    },
    "new york": {
        "accommodation": 200.0,
        "food": 70.0,
        "transport": 25.0,
        "activities": 55.0,
        "miscellaneous": 30.0,
    },
    "marrakech": {
        "accommodation": 60.0,
        "food": 25.0,
        "transport": 10.0,
        "activities": 30.0,
        "miscellaneous": 15.0,
    },
}

# Rough round-trip flight estimates from a generic origin (USD)
FLIGHT_ESTIMATES: dict[str, float] = {
    "barcelona": 450.0,
    "paris": 500.0,
    "tokyo": 900.0,
    "new york": 350.0,
    "marrakech": 400.0,
}

DEFAULT_DAILY_COST = {
    "accommodation": 130.0,
    "food": 55.0,
    "transport": 18.0,
    "activities": 40.0,
    "miscellaneous": 20.0,
}
DEFAULT_FLIGHT = 600.0


@mcp.tool()
def estimate_budget(destination: str, days: int) -> str:
    """
    Estimate total travel budget in USD for a given destination and number
    of days. Returns itemized daily costs plus round-trip flight estimate.
    """
    key = destination.strip().lower()

    profile = COST_PROFILES.get(key, DEFAULT_DAILY_COST)
    flight = FLIGHT_ESTIMATES.get(key, DEFAULT_FLIGHT)

    daily_total = sum(profile.values())
    total_daily = daily_total * days
    grand_total = total_daily + flight

    breakdown = "\n".join(
        f"  • {cat.title()}: ${cost:.2f}/day × {days} days = ${cost * days:.2f}"
        for cat, cost in profile.items()
    )

    return (
        f"=== Budget Estimate for {destination.title()} ({days} days) ===\n\n"
        f"Daily Cost Breakdown:\n{breakdown}\n\n"
        f"Daily Total: ${daily_total:.2f}\n"
        f"Total for {days} days: ${total_daily:.2f}\n"
        f"Round-trip Flight Estimate: ${flight:.2f}\n"
        f"─────────────────────────────\n"
        f"Grand Total: ${grand_total:.2f} USD"
    )


@mcp.tool()
def get_daily_cost(destination: str) -> str:
    """Get the average daily cost breakdown for a destination."""
    key = destination.strip().lower()
    profile = COST_PROFILES.get(key, DEFAULT_DAILY_COST)
    daily_total = sum(profile.values())

    lines = [f"  • {cat.title()}: ${cost:.2f}" for cat, cost in profile.items()]
    return (
        f"Daily costs in {destination.title()}:\n"
        + "\n".join(lines)
        + f"\n  Total: ${daily_total:.2f}/day"
    )


if __name__ == "__main__":
    mcp.run(transport="sse", host="localhost", port=3002)
