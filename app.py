# app.py - Streamlit UI for the Retail POS LLM Assistant
import os
import pathlib
import streamlit as st
from ingest import build_store
from rag import make_chain
from agents import price_lookup, inventory_check, issue_ticket

st.set_page_config(page_title="Retail POS LLM Assistant", page_icon="🧾")
st.title("Retail POS LLM Assistant 🧾")
st.caption("RAG + simple agentic tools for retail POS scenarios")

# --- Ensure API key is available on Cloud (st.secrets) or local env
OPENAI_KEY = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
if OPENAI_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY
else:
    st.warning("Missing OPENAI_API_KEY. Add it in Streamlit Secrets or your environment.")

# --- Auto-ingest if vector store missing (first run on Streamlit Cloud)
DB_DIR = "vector_store"
def _needs_ingest(db_dir: str) -> bool:
    p = pathlib.Path(db_dir)
    return (not p.exists()) or (p.exists() and not any(p.iterdir()))

if _needs_ingest(DB_DIR):
    with st.spinner("Building vector store (first run)…"):
        try:
            build_store()
            st.success("Vector store ready.")
        except Exception as e:
            st.error("Ingest failed. Ensure knowledge_base/*.md exist and have content.")
            st.exception(e)


# --- Build (and cache) the chain
@st.cache_resource(show_spinner=False)
def get_chain():
    return make_chain()

if "chain" not in st.session_state:
    st.session_state.chain = get_chain()

with st.form("qa_form", clear_on_submit=False):
    q = st.text_input("Ask about POS ops, coupons, troubleshooting, etc.")
    submitted = st.form_submit_button("Answer")
    if submitted and q:
        try:
            answer = st.session_state.chain(q)
            st.markdown(answer)
        except Exception as e:
            st.error("There was an error generating an answer. Check that your OPENAI_API_KEY is set.")
            st.exception(e)

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    sku = st.text_input("SKU for price lookup", placeholder="SKU123", key="sku1")
    if st.button("Price Lookup"):
        st.json(price_lookup(sku))

with col2:
    store = st.text_input("Store ID", placeholder="RTP-001", key="store1")
    sku2 = st.text_input("SKU for inventory", placeholder="SKU456", key="sku2")
    if st.button("Inventory Check"):
        st.json(inventory_check(store, sku2))

with col3:
    summary = st.text_input("Issue Summary", placeholder="POS freeze during payment", key="sum1")
    if st.button("Open Ticket"):
        st.json(issue_ticket(summary))

st.markdown(
    "**Notes**  \n"
    "- On first run, the app auto-builds the Chroma vector store from `knowledge_base/`.  \n"
    "- Set `OPENAI_API_KEY` in Streamlit **Secrets** or as an environment variable.  \n"
)
