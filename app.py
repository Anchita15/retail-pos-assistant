import os, shutil, pathlib
import streamlit as st

from ingest import build_store, KB_DIR, DB_DIR
from rag import make_chain
from agents import price_lookup, inventory_check, issue_ticket

st.set_page_config(page_title="Retail POS LLM Assistant", page_icon="🧾", layout="wide")

# --- Status panel
openai_ok = bool(st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
groq_ok = bool(st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY")))  # optional
vecdb_ok = pathlib.Path(DB_DIR).exists() and any(pathlib.Path(DB_DIR).iterdir())

st.sidebar.title("Status")
st.sidebar.write(f"**GROQ key:** {'✅' if groq_ok else '❌'}")
st.sidebar.write(f"**OpenAI key:** {'✅' if openai_ok else '❌'}")
st.sidebar.write(f"**Vector DB:** {'✅' if vecdb_ok else '❌'}")
st.sidebar.caption("Tip: Add keys in App → Settings → Secrets.")

st.title("Retail POS LLM Assistant 🧾")
st.caption("RAG + simple agentic tools for retail POS scenarios")

# --- Helpers
def _needs_ingest(db_dir: str) -> bool:
    d = pathlib.Path(db_dir)
    return (not d.exists()) or (not any(d.iterdir()))

# Build (and cache) the chain
@st.cache_resource(show_spinner=False)
def _chain():
    return make_chain(DB_DIR)

# Ensure a usable vector store
if _needs_ingest(DB_DIR):
    with st.spinner("Building vector store (first run)…"):
        build_store()

# auto-repair stale/corrupt Chroma (version mismatch)
try:
    st.session_state.chain = _chain()
except Exception:
    shutil.rmtree(DB_DIR, ignore_errors=True)
    with st.spinner("Vector DB looked stale; rebuilding…"):
        build_store()
    st.session_state.chain = _chain()

# --- UI
st.subheader("Ask the POS assistant")
q = st.text_input("Your question", placeholder="e.g., What are key POS components?")
go = st.button("Ask")

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("Agent tools (demo)")
    sku = st.text_input("SKU", value="SKU-1001")
    if st.button("Price lookup"):
        st.write(price_lookup(sku))
    if st.button("Inventory check"):
        st.write(inventory_check(sku))
    if st.button("Open issue ticket"):
        st.write(issue_ticket(title=f"Issue with {sku}", detail="Scanner not reading"))

with col1:
    if go and q.strip():
        if not openai_ok:
            st.error("OPENAI_API_KEY is missing. Add it in App → Settings → Secrets.")
        else:
            with st.spinner("Thinking…"):
                try:
                    answer = st.session_state.chain(q)
                    st.markdown(answer)
                except Exception as e:
                    st.error("There was an error generating an answer. Check logs.")
                    st.exception(e)

st.divider()
with st.expander("Knowledge base files available"):
    kb_files = sorted([str(p) for p in pathlib.Path(KB_DIR).glob("**/*.md")])
    if kb_files:
        st.code("\n".join(kb_files), language="text")
    else:
        st.write("No KB files found.")
