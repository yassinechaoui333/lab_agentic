"""
src/agent/agent.py – LangChain Agentic Travel Planner powered by Ollama + MCP tools.

This module provides:
  • run_travel_agent()  – main async entry point (Exercise 1 + 3)
  • run_critic_agent()  – validates a generated plan (Exercise 2)

MCP servers are assumed to be running on localhost:3001-3005.
Start them with:  python scripts/run_servers.py
"""

import asyncio
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

# ── MCP server endpoints ─────────────────────────────────────────────────── #

MCP_SERVERS: dict[str, dict[str, str]] = {
    "travel-search": {
        "url": "http://localhost:3001/sse",
        "transport": "sse",
    },
    "finance": {
        "url": "http://localhost:3002/sse",
        "transport": "sse",
    },
    "weather": {
        "url": "http://localhost:3003/sse",
        "transport": "sse",
    },
    "currency": {
        "url": "http://localhost:3004/sse",
        "transport": "sse",
    },
    "calculator": {
        "url": "http://localhost:3005/sse",
        "transport": "sse",
    },
}

# ── System prompt ─────────────────────────────────────────────────────────── #

SYSTEM_PROMPT = """\
You are an expert travel planning assistant. Your job is to help users plan
amazing trips by gathering information from your available tools.

**Available tools:**
- search_destination / list_available_destinations – find attractions & activities
- estimate_budget / get_daily_cost – calculate travel costs
- get_weather / get_best_months – check weather conditions
- convert_currency / list_currencies – convert costs to user's currency
- calculate / percentage / split_cost – arithmetic operations

**How to work:**
1. Understand the user's request (destination, dates, budget, preferences).
2. Use search_destination to find attractions and activities.
3. Use estimate_budget to calculate costs.
4. Use get_weather if the user mentions dates or a month – adapt activities
   to weather (prefer indoor activities on rainy months).
5. Use convert_currency if the user mentions a non-USD currency.
6. Use calculate when you need precise arithmetic.
7. Synthesize everything into a clear, day-by-day travel itinerary.

Always be helpful, specific, and provide a structured plan.\
"""

CRITIC_PROMPT = """\
You are a travel plan critic. Review the following travel plan and provide:
1. **Feasibility score** (1-10): Is the plan realistic and achievable?
2. **Budget assessment**: Is the budget reasonable for the destination?
3. **Activity balance**: Good mix of culture, food, relaxation, adventure?
4. **Potential issues**: Weather conflicts, overly packed schedule, missing essentials?
5. **Suggestions**: 2-3 concrete improvements.

Be concise and constructive.\
"""


# ── Agent runner ──────────────────────────────────────────────────────────── #

async def run_travel_agent(
    user_request: str,
    model: str = "llama3.1",
    budget_limit: float | None = None,
) -> dict[str, Any]:
    """
    Run the travel planning agent.

    Returns a dict with:
      - "output": final text answer
      - "tool_calls": list of {tool_name, tool_input, tool_output} dicts
      - "messages": raw message list from langgraph
    """
    llm = ChatOllama(model=model, temperature=0.3)

    prompt = user_request
    if budget_limit is not None:
        prompt += (
            f"\n\n⚠️ IMPORTANT: The user has a strict maximum budget of "
            f"${budget_limit:.2f} USD. You MUST keep the total trip cost "
            f"under this amount. If the initial estimate exceeds the budget, "
            f"suggest cheaper alternatives or reduce the number of days."
        )

    async with MultiServerMCPClient(MCP_SERVERS) as client:
        tools = client.get_tools()
        agent = create_react_agent(llm, tools)

        result = await agent.ainvoke({
            "messages": [
                ("system", SYSTEM_PROMPT),
                ("user", prompt),
            ]
        })

    # Parse messages to extract tool calls
    messages = result.get("messages", [])
    tool_calls_log: list[dict[str, str]] = []
    output = ""

    for msg in messages:
        # AIMessage with tool_calls
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls_log.append({
                    "tool_name": tc.get("name", "unknown"),
                    "tool_input": str(tc.get("args", {})),
                    "tool_output": "",  # filled below
                })
        # ToolMessage (response from a tool)
        if msg.type == "tool":
            if tool_calls_log and not tool_calls_log[-1]["tool_output"]:
                tool_calls_log[-1]["tool_output"] = msg.content
        # Last AI message = final answer
        if msg.type == "ai" and not getattr(msg, "tool_calls", None):
            output = msg.content

    return {
        "output": output or str(messages[-1].content if messages else ""),
        "tool_calls": tool_calls_log,
        "messages": messages,
    }


async def run_critic_agent(
    travel_plan: str,
    model: str = "llama3.1",
) -> str:
    """Run the critic agent on a generated travel plan (Exercise 2)."""
    llm = ChatOllama(model=model, temperature=0.2)
    response = await llm.ainvoke([
        ("system", CRITIC_PROMPT),
        ("user", f"Please review this travel plan:\n\n{travel_plan}"),
    ])
    return response.content


# ── Synchronous wrapper for Streamlit ─────────────────────────────────────── #

def run_travel_agent_sync(
    user_request: str,
    model: str = "llama3.1",
    budget_limit: float | None = None,
) -> dict[str, Any]:
    """Synchronous wrapper around run_travel_agent."""
    import nest_asyncio
    nest_asyncio.apply()
    return asyncio.run(run_travel_agent(user_request, model, budget_limit))


def run_critic_agent_sync(travel_plan: str, model: str = "llama3.1") -> str:
    """Synchronous wrapper around run_critic_agent."""
    import nest_asyncio
    nest_asyncio.apply()
    return asyncio.run(run_critic_agent(travel_plan, model))


# ── CLI entry point ───────────────────────────────────────────────────────── #

if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or (
        "Plan a 5-day trip to Barcelona with an estimated budget "
        "and suggested activities."
    )
    print(f"🌍 Query: {query}\n")

    result = run_travel_agent_sync(query)

    print("═" * 60)
    print("🔧 Tool Calls Made:")
    for i, tc in enumerate(result["tool_calls"], 1):
        print(f"  {i}. {tc['tool_name']}({tc['tool_input']})")
    print("═" * 60)
    print("\n📋 Travel Plan:\n")
    print(result["output"])
