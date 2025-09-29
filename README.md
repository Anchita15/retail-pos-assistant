# Retail POS LLM Assistant (StoreOps Copilot)

An original Streamlit app demonstrating **LLM integration**, **RAG** with a local vector store, and simple **agentic tools** (price lookup, inventory check, ticketing) aligned with retail POS use-cases.

## Tech
- Streamlit UI • LangChain • Chroma • SentenceTransformers
- Optional: OpenAI for generation (swap to any LangChain-compatible LLM if preferred)

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python ingest.py
streamlit run app.py
