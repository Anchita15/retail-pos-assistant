# app.py — Retail POS LLM Assistant (Streamlit)
# - Auto-ingests knowledge_base on first run
# - Uses OPENAI_API_KEY from st.secrets or env
# - Graceful errors for 401/429
# - Simple agentic demo tools (price lookup, inventory, ticket)

import os
import pathlib
import streamlit as st

# Local modules
from ingest import build_store
from rag import make_chain
from agents import price_lookup, inventory_check, issue_ticket

# ---------------------- Page setup ----------------------
st.set_page_config(page_title="Retail POS LLM Assistant", page_icon="🧾")
st.title("Retail POS LLM Assistant 🧾")
st.caption("RAG + simple agentic tools for retail POS scenarios")

# ---------------------- Secrets / API key ----------------------
# Prefer Streamlit Cloud Secrets; fallback to environment variable
OPENAI_KEY = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
if OPENAI_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY
else:
    st.warning(
        "Missing OPENAI_API_KEY. Add it in Streamlit **Settings → Secrets** or set an environment variable."
    )

# ---------------------- Auto-ingest on first run ----------------------
DB_DIR = "vector_store"

def _needs_ingest(db_dir: str) -> bool:
    p = pathlib.Path(db_dir)
    # If directory doesn't exist, or exists but is empty
    return (not p.exists()) or (p.exists() and not any(p.iterdir()))

if _needs_ingest(DB_DIR):
    with st.spinner("Building vector store (first run)…"):
        try:
            build_store()  # robust ingest creates a starter.md if KB is empty
            st.success("Vector store ready.")
        except Exception as e:
            st.error("Ingest failed. Ensure `knowledge_base/*.md` exist and contain text.")
            st.exception(e)

# ---------------------- Build (and cache) the chain ----------------------
@st.cache_resource(show_spinner=False)
def get_chain():
    return make_chain()

try:
    if "chain" not in st.session_state:
        st.session_state.chain = get_chain()
except Exception as e:
    # If chain creation failed (e.g., missing key), surface a helpful message
    st.error(
        "Failed to initialize the LLM chain. Verify OPENAI_API_KEY and see logs."
    )
    st.exception(e)

# ---------------------- Q&A form ----------------------
with st.form("qa_form", clear_on_submit=False):
    q = st.text_input("Ask about POS ops, coupons, troubleshooting, etc.")
    submitted = st.form_submit_button("Answer")
    if submitted and q:
        try:
            answer = st.session_state.chain(q)
            # Chain returns a string (from rag.make_chain)
            st.markdown(answer)
        except Exception as e:
            msg = str(e)
            # Friendly errors for common auth/quota issues
            if "invalid_api_key" in msg or "401" in msg:
                st.error("Invalid or missing OpenAI API key (401). Check your OPENAI_API_KEY.")
            elif "insufficient_quota" in msg or "RateLimitError" in msg or "429" in msg:
                st.error("Your OpenAI account has run out of credit (429). Add billing or use a different API key.")
            else:
                st.error("There was an error generating an answer. See logs for details.")
            st.exception(e)

st.markdown("---")

# ---------------------- Tool demos ----------------------
col1, col2, col3 = st.columns(3)

with col1:
    sku = st.text_input("SKU for price lookup", placeholder="SKU123", key="sku1")
    if st.button("Price Lookup"):
        try:
            st.json(price_lookup(sku))
        except Exception as e:
            st.error("Price lookup failed.")
            st.exception(e)

with col2:
    store = st.text_input("Store ID", placeholder="RTP-001", key="store1")
    sku2 = st.text_input("SKU for inventory", placeholder="SKU456", key="sku2")
    if st.button("Inventory Check"):
        try:
            st.json(inventory_check(store, sku2))
        except Exception as e:
            st.error("Inventory check failed.")
            st.exception(e)

with col3:
    summary = st.text_input("Issue Summary", placeholder="POS freeze during payment", key="sum1")
    if st.button("Open Ticket"):
        try:
            st.json(issue_ticket(summary))
        except Exception as e:
            st.error("Ticket creation failed.")
            st.exception(e)

# ---------------------- Help text ----------------------
st.markdown(
    "**Notes**  \n"
    "- On first run, the app auto-builds the Chroma vector store from `knowledge_base/`.  \n"
    "- Set `OPENAI_API_KEY` in Streamlit **Secrets** or as an environment variable.  \n"
)
