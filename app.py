# app.py — Retail POS LLM Assistant (Streamlit)
import os, shutil, pathlib
import streamlit as st

from ingest import build_store
from rag import make_chain
from agents import price_lookup, inventory_check, issue_ticket

st.set_page_config(page_title="Retail POS LLM Assistant", page_icon="🧾")
st.title("Retail POS LLM Assistant 🧾")
st.caption("RAG + simple agent tools for POS scenarios")

# --- OpenAI key (from env or Streamlit secrets)
OPENAI_KEY = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
if OPENAI_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY
else:
    st.info("Tip: set OPENAI_API_KEY in Streamlit Secrets for LLM answers. "
            "Without it, the app answers from the KB only (fallback).")

DB_DIR = "vector_store"

def _needs_ingest(db_dir: str) -> bool:
    p = pathlib.Path(db_dir)
    return (not p.exists()) or (p.exists() and not any(p.iterdir()))

with st.expander("⚙️ Index controls"):
    if st.button("Rebuild knowledge index"):
        if pathlib.Path(DB_DIR).exists():
            shutil.rmtree(DB_DIR)
        with st.spinner("Rebuilding index..."):
            build_store()
        st.success("Index rebuilt.")

if _needs_ingest(DB_DIR):
    with st.spinner("Building vector store (first run)…"):
        build_store()
        st.success("Vector store ready.")

@st.cache_resource(show_spinner=False)
def get_chain():
    return make_chain()

st.session_state.setdefault("chain", get_chain())

with st.form("qa", clear_on_submit=False):
    q = st.text_input("Ask about POS ops, coupons, troubleshooting, etc.")
    ask = st.form_submit_button("Answer")
    if ask and q:
        try:
            st.markdown(st.session_state.chain(q))
        except Exception as e:
            st.error("Error generating answer. See logs.")
            st.exception(e)

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    sku = st.text_input("SKU (price lookup)", "SKU123")
    if st.button("Price Lookup"):
        st.json(price_lookup(sku))

with col2:
    store = st.text_input("Store ID", "RTP-001")
    sku2 = st.text_input("SKU (inventory)", "SKU456")
    if st.button("Inventory Check"):
        st.json(inventory_check(store, sku2))

with col3:
    summary = st.text_input("Issue Summary", "POS freeze during payment")
    if st.button("Open Ticket"):
        st.json(issue_ticket(summary))

# --- KB Debug (helps verify what the app sees)
with st.expander("🔍 KB Debug"):
    import pathlib
    kb = pathlib.Path("knowledge_base")
    if not kb.exists():
        st.error("knowledge_base/ not found")
    else:
        files = list(kb.glob("*.md"))
        st.write(f"Found {len(files)} markdown files:")
        for p in files:
            text = p.read_text(encoding="utf-8")
            preview = (text.strip()[:300] + "…") if len(text) > 300 else text
            st.markdown(f"- **{p.name}** ({len(text)} chars)\n\n> {preview}")
