"""
src/agent/app.py – Streamlit GUI for the Agentic Travel Planning Assistant.

Implements all 3 exercises:
  1. Display each tool call in the GUI
  2. Critic agent to validate itineraries
  3. Budget constraint with automatic re-planning

Run:  streamlit run src/agent/app.py
      (from the project root, with MCP servers running via scripts/run_servers.py)
"""

import streamlit as st
from src.agent.agent import run_travel_agent_sync, run_critic_agent_sync

# ── Page config ───────────────────────────────────────────────────────────── #

st.set_page_config(
    page_title="Agentic Travel Planner",
    page_icon="🌍",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────── #

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.05rem;
    }

    .tool-card {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .tool-name {
        color: #89b4fa;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .tool-input {
        color: #a6adc8;
        font-size: 0.85rem;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 0.3rem;
    }

    .critic-box {
        background: linear-gradient(135deg, #1e1e2e 0%, #181825 100%);
        border: 1px solid #f5c2e7;
        border-radius: 12px;
        padding: 1.2rem;
        margin-top: 1rem;
    }

    .stat-box {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #313244;
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #89b4fa;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #a6adc8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #313244;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────── #

st.markdown("""
<div class="main-header">
    <h1>🌍 Agentic Travel Planner</h1>
    <p>AI-powered trip planning using LangChain agents with MCP tool servers</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar settings ─────────────────────────────────────────────────────── #

with st.sidebar:
    st.markdown("## ⚙️ Settings")

    model = st.selectbox(
        "Ollama Model",
        ["llama3.1", "llama3.2", "mistral", "gemma2", "qwen2.5"],
        index=0,
        help="Select the Ollama model to use for the agent.",
    )

    st.markdown("---")
    st.markdown("### 💰 Budget Constraint")
    enable_budget = st.toggle("Enable budget limit", value=False)
    budget_limit = None
    if enable_budget:
        budget_limit = st.number_input(
            "Maximum budget (USD)",
            min_value=100.0,
            max_value=50000.0,
            value=2000.0,
            step=100.0,
        )

    st.markdown("---")
    st.markdown("### 🔍 Critic Agent")
    enable_critic = st.toggle(
        "Enable plan validation",
        value=True,
        help="A critic agent reviews the generated plan for feasibility.",
    )

    st.markdown("---")
    st.markdown("### 📡 MCP Servers")
    st.markdown("""
    Make sure all servers are running:
    ```bash
    python run_servers.py
    ```

    | Server | Port |
    |--------|------|
    | Travel Search | 3001 |
    | Finance | 3002 |
    | Weather | 3003 |
    | Currency | 3004 |
    | Calculator | 3005 |
    """)

# ── Main content ──────────────────────────────────────────────────────────── #

# Example prompts
examples = [
    "Plan a 5-day trip to Barcelona with an estimated budget and suggested activities.",
    "I want to visit Tokyo for a week in April. What's the weather like and what should I do?",
    "Plan a budget-friendly 4-day trip to Marrakech. Convert costs to EUR.",
    "Compare Paris and New York for a 3-day trip – which is cheaper?",
]

st.markdown("### ✈️ Plan Your Trip")

selected_example = st.selectbox(
    "Try an example prompt:",
    ["Custom query..."] + examples,
)

if selected_example != "Custom query...":
    query = st.text_area(
        "Your travel request",
        value=selected_example,
        height=100,
        label_visibility="collapsed",
    )
else:
    query = st.text_area(
        "Your travel request",
        placeholder="Describe your ideal trip... e.g., 'Plan a 5-day trip to Barcelona with budget and activities'",
        height=100,
        label_visibility="collapsed",
    )

# ── Run agent ─────────────────────────────────────────────────────────────── #

if st.button("🚀 Plan My Trip", type="primary", use_container_width=True):
    if not query or not query.strip():
        st.warning("Please enter a travel request.")
        st.stop()

    # Run the main agent
    with st.status("🤖 Agent is working...", expanded=True) as status:
        st.write("🔗 Connecting to MCP servers...")
        st.write("🧠 Agent is reasoning and selecting tools...")

        try:
            result = run_travel_agent_sync(query, model=model, budget_limit=budget_limit)
        except Exception as e:
            st.error(f"❌ Agent error: {e}")
            st.info(
                "Make sure Ollama is running (`ollama serve`) and all MCP servers "
                "are started (`python run_servers.py`)."
            )
            st.stop()

        status.update(label="✅ Plan generated!", state="complete")

    # ── Stats row ──────────────────────────────────────────────────────── #
    tool_calls = result.get("tool_calls", [])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(tool_calls)}</div>
            <div class="stat-label">Tool Calls</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        unique_tools = len(set(tc["tool_name"] for tc in tool_calls))
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{unique_tools}</div>
            <div class="stat-label">Unique Tools</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(result.get("messages", []))}</div>
            <div class="stat-label">Messages</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Two-column layout ──────────────────────────────────────────────── #
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.markdown("### 📋 Travel Plan")
        st.markdown(result["output"])

    with right_col:
        # Exercise 1: Display each tool call
        st.markdown("### 🔧 Tool Calls")
        if tool_calls:
            for i, tc in enumerate(tool_calls, 1):
                with st.expander(f"🛠 {i}. {tc['tool_name']}", expanded=False):
                    st.markdown(f"**Input:**")
                    st.code(tc["tool_input"], language="json")
                    if tc["tool_output"]:
                        st.markdown(f"**Output:**")
                        st.text(tc["tool_output"][:500])
        else:
            st.info("No tool calls were made by the agent.")

    # ── Exercise 2: Critic agent ───────────────────────────────────────── #
    if enable_critic and result["output"]:
        st.markdown("---")
        st.markdown("### 🧐 Critic Agent Review")
        with st.spinner("Critic agent is reviewing the plan..."):
            try:
                critique = run_critic_agent_sync(result["output"], model=model)
                st.markdown(f"""<div class="critic-box">{critique}</div>""",
                            unsafe_allow_html=True)
                st.markdown(critique)
            except Exception as e:
                st.warning(f"Critic agent failed: {e}")

    # ── Exercise 3: Budget enforcement ─────────────────────────────────── #
    if enable_budget and budget_limit:
        st.markdown("---")
        st.markdown(f"### 💰 Budget Constraint: ${budget_limit:,.2f} USD")
        st.info(
            f"The agent was instructed to keep the total cost under "
            f"${budget_limit:,.2f}. If the plan exceeds this, click below "
            f"to re-plan with tighter constraints."
        )
        if st.button("🔄 Re-plan with Tighter Budget", use_container_width=True):
            tighter_request = (
                f"{query}\n\nCRITICAL: The previous plan was too expensive. "
                f"You MUST keep total costs under ${budget_limit:.2f} USD. "
                f"Use cheaper accommodation, reduce activities, or shorten the trip."
            )
            with st.spinner("Re-planning with tighter budget..."):
                try:
                    result2 = run_travel_agent_sync(
                        tighter_request, model=model, budget_limit=budget_limit * 0.9
                    )
                    st.markdown("### 📋 Revised Plan")
                    st.markdown(result2["output"])
                except Exception as e:
                    st.error(f"Re-planning failed: {e}")

# ── Footer ────────────────────────────────────────────────────────────────── #

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#6c7086; font-size:0.85rem;'>"
    "Built with LangChain · MCP · Ollama · Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
