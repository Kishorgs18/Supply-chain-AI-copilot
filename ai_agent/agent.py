"""Agentic supply-chain copilot: a LangGraph ReAct agent (Groq Llama 3.1) with
two tools — SQL over a DuckDB warehouse and an XGBoost delay predictor.

Importable: call `get_agent()` to build the agent (after GROQ_API_KEY is set).
Run directly (`python ai_agent/agent.py`) for a CLI chat loop.
"""
import pickle
from pathlib import Path

import duckdb
import pandas as pd
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "supply_chain.duckdb"
SNAPSHOT = ROOT / "supply_chain_snapshot.duckdb"
MODEL = ROOT / "notebooks" / "delay_prediction_model.pkl"
FEATURES = ROOT / "notebooks" / "model_features.pkl"


@tool
def query_warehouse(sql_query: str) -> str:
    """Executes a SQL query against the DuckDB warehouse (table: fct_orders).
    Use it for questions about orders, revenue, or historical delays.
    Example: SELECT SUM(total_amount) FROM fct_orders;"""
    con = None
    try:
        # Copy to a detached snapshot to bypass any active write-locks.
        with open(DB, "rb") as fi, open(SNAPSHOT, "wb") as fo:
            fo.write(fi.read())
        con = duckdb.connect(str(SNAPSHOT), read_only=True)
        if not sql_query or len(sql_query.strip()) < 5:
            return "Error: Invalid or empty SQL query provided."
        return con.execute(sql_query).df().to_string()
    except Exception as e:
        return f"Database error: {e}. Do not re-try or loop; report it to the user."
    finally:
        if con:
            try:
                con.close()
            except Exception:
                pass


@tool
def predict_order_delay(category: str, country: str) -> str:
    """Predicts whether a hypothetical order is likely to be delayed (XGBoost).
    Use it when asked if a new/future order will be late."""
    try:
        model = pickle.load(open(MODEL, "rb"))
        features = pickle.load(open(FEATURES, "rb"))
        x = pd.DataFrame(0, index=[0], columns=features)
        for col in (f"product_category_{category}", f"destination_country_{country}"):
            if col in x.columns:
                x[col] = 1
        return "High risk of delay!" if model.predict(x)[0] == 1 else "Likely to ship on time."
    except Exception as e:
        return f"Prediction Error: {e}"


SYSTEM_PROMPT = """You are an elite Supply Chain Analytics executive with access to a DuckDB warehouse.

The ONLY table is `fct_orders`, with these columns and EXACT allowed values:
- order_id, customer_id, product_id : text
- product_category : one of 'Furniture', 'Electronics', 'Apparel', 'Home Goods'
- quantity : integer
- total_amount : float (revenue)
- destination_country : one of 'US', 'UK', 'DE', 'FR', 'JP', 'CA', 'AU'
- order_status : one of 'processing', 'shipped', 'delayed', 'delivered'  (lowercase)
- order_placed_at : timestamp
- is_delayed : 1 if delayed else 0

Rules:
- Write ONE clean, valid DuckDB SQL query using ONLY the exact values above. Never invent status values.
- For delayed orders use:  WHERE order_status = 'delayed'  (or is_delayed = 1).
- If a tool returns an error, STOP immediately — do not retry or loop. Present the result or error to the manager clearly and concisely."""

TOOLS = [query_warehouse, predict_order_delay]


def get_agent(model_name: str = "llama-3.3-70b-versatile"):
    """Build the ReAct agent. Requires GROQ_API_KEY in the environment."""
    llm = ChatGroq(model=model_name, temperature=0)
    return create_react_agent(llm, TOOLS, prompt=SYSTEM_PROMPT)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = get_agent()
    print("Supply Chain AI Agent online. Type 'exit' to quit.\n" + "-" * 50)
    while True:
        user_input = input("\nManager: ")
        if user_input.lower() in ("quit", "exit", "q"):
            break
        for event in agent.stream({"messages": [("user", user_input)]}, stream_mode="values"):
            msg = event["messages"][-1]
            if msg.type == "ai" and msg.content:
                print(f"\nAgent: {msg.content}")
            elif msg.type == "tool":
                print(f"   [Used Tool: {msg.name}]")
