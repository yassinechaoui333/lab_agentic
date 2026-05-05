# 🌍 Agentic Travel Planner

> An AI-powered travel planning assistant built with **LangChain**, **LangGraph**, **Ollama**, and the **Model Context Protocol (MCP)**.

---

## Project Structure

```
lab-agentic/
├── src/
│   ├── agent/
│   │   ├── __init__.py          # Public API exports
│   │   ├── agent.py             # LangChain ReAct agent + critic
│   │   └── app.py               # Streamlit web UI
│   └── mcp_servers/
│       ├── __init__.py
│       ├── travel_search_server.py  # Port 3001 – destinations & attractions
│       ├── finance_server.py        # Port 3002 – budget estimation
│       ├── weather_server.py        # Port 3003 – weather & best months
│       ├── currency_server.py       # Port 3004 – currency conversion
│       └── calculator_server.py     # Port 3005 – arithmetic
├── scripts/
│   └── run_servers.py           # Launch all 5 MCP servers
├── tests/                       # Unit & integration tests
├── docs/                        # Documentation & report
├── main.py                      # Minimal CLI entry point
├── pyproject.toml               # Project metadata & dependencies
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
pip install -e .
```

### 2. Start Ollama

```bash
ollama serve
ollama pull llama3.1
```

### 3. Launch MCP tool servers

```bash
python scripts/run_servers.py
```

| Server | Port | Tools |
|---|---|---|
| Travel Search | 3001 | `search_destination`, `list_available_destinations` |
| Finance | 3002 | `estimate_budget`, `get_daily_cost` |
| Weather | 3003 | `get_weather`, `get_best_months` |
| Currency | 3004 | `convert_currency`, `list_currencies` |
| Calculator | 3005 | `calculate`, `percentage`, `split_cost` |

### 4. Run the Streamlit app

```bash
streamlit run src/agent/app.py
```

---

## Architecture

The system follows a **ReAct (Reason + Act)** agentic loop:

```
User Query
    │
    ▼
LangGraph ReAct Agent (llama3.1 via Ollama)
    │  reasons about query
    │  selects tool(s)
    ▼
MCP Tool Servers  ←──── SSE transport (localhost)
    │  returns structured results
    ▼
Agent synthesizes final answer
    │
    ▼  (optional)
Critic Agent  ─── reviews feasibility, budget, activity balance
```

## Exercises

| # | Feature | Implementation |
|---|---|---|
| 1 | **Tool Call Transparency** | Each MCP call is logged and shown in the Streamlit sidebar |
| 2 | **Critic Agent** | A second LLM pass reviews feasibility, budget, and activity balance |
| 3 | **Budget Constraint** | Agent is instructed to stay under a user-defined USD limit; one-click re-planning if over budget |

## Dependencies

- `langchain >= 0.3` – LLM orchestration
- `langgraph >= 0.4` – ReAct agent graph
- `langchain-ollama` – Ollama LLM adapter
- `langchain-mcp-adapters` – MCP ↔ LangChain tool bridge
- `mcp[cli] >= 1.0` – Model Context Protocol servers
- `streamlit >= 1.40` – Web UI
