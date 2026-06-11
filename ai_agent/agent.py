import os
import duckdb
import pickle
import pandas as pd
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_groq import ChatGroq
# Updated import path to get rid of the deprecation warning
from langgraph.prebuilt import create_react_agent 

# Load API Key
load_dotenv('../.env')

print("Booting up Agentic Tools...")

@tool
def query_warehouse(sql_query: str) -> str:
    """
    Executes a SQL query against the DuckDB Data Warehouse.
    Use this to answer questions about past orders, revenue, or historical delays.
    The main table is called 'fct_orders'.
    
    CRITICAL: ALWAYS use clean SQL syntax. Example to get total revenue:
    SELECT SUM(total_amount) FROM fct_orders;
    """
    src = '../supply_chain.duckdb'
    dst = '../supply_chain_snapshot.duckdb'
    con = None
    
    try:
        # Read byte-stream directly to completely bypass active process OS locks
        with open(src, 'rb') as f_in:
            with open(dst, 'wb') as f_out:
                f_out.write(f_in.read())
                
        con = duckdb.connect(dst, read_only=True)
        
        if not sql_query or len(sql_query.strip()) < 5:
            return "Error: Invalid or empty SQL query provided."
            
        result = con.execute(sql_query).df()
        return result.to_string()
        
    except Exception as e:
        return f"Database error occurred: {str(e)}. Do not re-try or loop. Report this issue to the user directly."
    finally:
        if con:
            try: con.close()
            except: pass

@tool
def predict_order_delay(category: str, country: str) -> str:
    """
    Predicts if a future order is likely to be delayed based on Machine Learning.
    Use this when the user asks if a new or hypothetical order will be late.
    """
    try:
        with open('../notebooks/delay_prediction_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('../notebooks/model_features.pkl', 'rb') as f:
            features = pickle.load(f)
            
        input_data = pd.DataFrame(0, index=[0], columns=features)
        cat_col = f"product_category_{category}"
        country_col = f"destination_country_{country}"
        
        if cat_col in input_data.columns: input_data[cat_col] = 1
        if country_col in input_data.columns: input_data[country_col] = 1
            
        prediction = model.predict(input_data)[0]
        return "High risk of delay!" if prediction == 1 else "Likely to ship on time."
    except Exception as e:
        return f"Prediction Error: {str(e)}"

# System prompt forcing the agent to act responsibly
system_prompt = """You are an elite Supply Chain Analytics executive. 
If a tool returns an error or a database lock warning, you must instantly stop executing tools. 
Do not loop or retry the same tool. Present whatever information or error you received directly to the manager."""

tools = [query_warehouse, predict_order_delay]
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

# FIX: Changed 'state_modifier' to 'prompt' to match modern LangGraph versions
agent_executor = create_react_agent(llm, tools, prompt=system_prompt)

print("Supply Chain AI Agent Online! Type 'exit' to quit.")
print("-" * 50)

while True:
    user_input = input("\nManager: ")
    if user_input.lower() in ['quit', 'exit', 'q']:
        break
        
    events = agent_executor.stream(
        {"messages": [("user", user_input)]},
        stream_mode="values"
    )
    
    for event in events:
        message = event["messages"][-1]
        if message.type == "ai" and message.content:
            print(f"\n Agent: {message.content}")
        elif message.type == "tool":
            print(f"   [Used Tool: {message.name}]")