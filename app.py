"""Streamlit chat UI for the Supply Chain AI Copilot.

Run locally:  streamlit run app.py   (with GROQ_API_KEY in a .env file)
On Streamlit Cloud: set GROQ_API_KEY in the app's Secrets.
"""
import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

st.set_page_config(page_title="Supply Chain AI Copilot", page_icon="📦", layout="centered")

# --- API key (from Streamlit secrets, env, or .env) -----------------------
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass
if not os.environ.get("GROQ_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

st.title("📦 Supply Chain AI Copilot")
st.caption(
    "An agentic AI (LangGraph + Groq Llama 3.3 70B) that answers supply-chain questions "
    "by querying a DuckDB warehouse and an XGBoost delay model."
)

if not os.environ.get("GROQ_API_KEY"):
    st.warning(
        "**GROQ_API_KEY not set.** Add it in the app's *Secrets* "
        "(`GROQ_API_KEY = \"...\"`). Get a free key at console.groq.com."
    )
    st.stop()

from ai_agent.agent import get_agent  # noqa: E402


@st.cache_resource(show_spinner="Booting the agent…")
def _agent():
    return get_agent()


agent = _agent()

with st.sidebar:
    st.header("Try asking")
    st.markdown(
        "- What is our total revenue?\n"
        "- How many orders are delayed?\n"
        "- Top 3 product categories by revenue?\n"
        "- Will an Electronics order to JP be delayed?\n"
        "- How many orders went to the UK?"
    )
    st.divider()
    st.caption("Data: 2,500 simulated orders in a DuckDB warehouse (`fct_orders`).")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ask the supply-chain copilot…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            tools_used = []
            answer = ""
            try:
                for event in agent.stream({"messages": [("user", prompt)]}, stream_mode="values"):
                    msg = event["messages"][-1]
                    if msg.type == "tool":
                        tools_used.append(msg.name)
                    elif msg.type == "ai" and msg.content:
                        answer = msg.content
            except Exception as e:
                answer = f"⚠️ Error: {e}"
            if tools_used:
                st.caption("🔧 Tools used: " + ", ".join(dict.fromkeys(tools_used)))
            st.markdown(answer or "_(no response)_")
    st.session_state.messages.append({"role": "assistant", "content": answer})
