"""
main.py – CLI entry point for the Agentic Travel Planner.

Usage:
    python main.py "Plan a 5-day trip to Barcelona"
    streamlit run src/agent/app.py   (for the web UI)
"""

import sys
from src.agent.agent import run_travel_agent_sync


def main():
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


if __name__ == "__main__":
    main()
