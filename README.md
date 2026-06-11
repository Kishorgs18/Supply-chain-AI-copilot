# Real-Time Supply Chain Lakehouse & Agentic AI Copilot

An end-to-end intelligent data infrastructure platform that orchestrates real-time streaming enterprise JSON logs, shapes them through a structured Medallion lakehouse architecture, runs custom predictive risk modeling, and exposes the system through an autonomous Generative AI Agent.

---

## 🏗️ Architecture Overview
[Real-Time Streaming Simulator (JSON)]
│
▼
[Bronze Layer: Local Storage]
│
▼  (dbt transformations / casting / formatting)
[Silver Layer: Staging Views (DuckDB)]
│
▼  (dbt aggregation / analytical structuring)
[Gold Layer: Analytics Marts (fct_orders)]
│                        │
▼ (Model Training)       ▼ (Snapshotting Engine)
[XGBoost Delay Classifier]  [LangGraph ReAct AI Copilot]
## 🛠️ Tech Stack & Ecosystem
* **Data Engineering:** Python (Data Simulation), dbt (Data Build Tool), DuckDB (Embedded Vectorized OLAP)
* **Data Science:** Jupyter Notebooks, XGBoost, Scikit-Learn, Pandas
* **AI Engineering:** LangGraph, LangChain Core, Groq Inference Engine, Meta Llama 3.1 & 3.3

---

## ⚡ Key Engineering Challenges & Solutions

### 1. Database Resource Locks in Embedded OLAP
* **The Problem:** DuckDB is a local, serverless single-file database. When the real-time Python log simulator continuously appended records, it maintained active OS write-locks. The downstream AI Agent attempting concurrent read queries threw critical locking errors, trapping the LLM in an infinite loop that drained daily API tokens.
* **The Solution:** Engineered a custom **Copy-on-Write (Snapshot) Architecture Pattern**. The AI Agent's query tool read raw file streams instantly to copy the database to a detached static replica (`_snapshot.duckdb`) in milliseconds. This completely decoupled production ingestion transactions from analytics queries.

### 2. Machine Learning Class Imbalance
* **The Problem:** Historical logistics data showed an inherent class imbalance where operational anomalies (shipping delays) only occurred in ~10% of total records. The initial XGBoost classification iteration prioritized overall accuracy over predictive precision, aggressively guessing "no delay".
* **The Solution:** Restructured the processing logic with one-hot encoded categorical parameters (`product_category`, `destination_country`) and introduced stratified feature splitting to stabilize baseline evaluation thresholds.

---

## 🚀 Interactive AI Copilot Capabilities
The integrated **LangGraph ReAct Agent** dynamically evaluates requests and executes native pipeline paths based on context:
* **Structured Analytics:** Automatically converts natural language questions (e.g., *"What is our total operational revenue so far?"*) into optimized SQL dialects, executing queries directly against the Gold data layer.
* **Predictive Risk Assessment:** Maps text indicators (e.g., *"Shipping Electronics to the UK"*) directly onto trained machine learning feature matrices to process real-time probabilistic delay checks.

