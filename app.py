# app.py - Streamlit UI for the Retail POS LLM Assistant
import os, shutil, pathlib
import streamlit as st
from ingest import build_store
from rag import make_chain

DB_DIR = "vector_store"
KB_DIR = "knowledge_base"

st.set_page_config(page_title="Retail POS LLM Assistant", page_icon="🧾", layout="centered")
st.title("Retail POS LLM Assistant 🧾")
st.caption("RAG + simple agentic tools for retail POS scenarios")

def _needs_ingest(db_dir: str) -> bool:
    p = pathlib.Path(db_dir)
    return not (p.exists() and any(p.iterdir()))

with st.sidebar:
    st.subheader("Status")
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    st.write(f"GROQ key: {'✅' if has_groq else '❌'}")
    st.write(f"OpenAI key: {'✅' if has_openai else '❌'}")
    st.write(f"Vector DB: {'✅' if not _needs_ingest(DB_DIR) else '❌'}")
    st.markdown("---")
    st.markdown("**Tip:** Add a GROQ or OpenAI key in **App → Settings → Secrets**.")

# Build the vector store on first boot (Cloud-safe)
if _needs_ingest(DB_DIR):
    with st.spinner("Building vector store (first run)…"):
        build_store()

@st.cache_resource(show_spinner=False)
def _chain():
    return make_chain(DB_DIR)

st.session_state.chain = _chain()

with st.form("ask"):
    q = st.text_input("Ask about POS ops, coupons, troubleshooting, etc.")
    submitted = st.form_submit_button("Answer")
    if submitted and q.strip():
        try:
            answer = st.session_state.chain(q.strip())
            st.markdown(answer)
        except Exception as e:
            # Friendly message for key/billing issues
            msg = str(e)
            if "insufficient_quota" in msg or "429" in msg:
                st.error("Your LLM provider quota was exceeded. Add a **GROQ_API_KEY** in Secrets to use the free Groq model.")
            elif "invalid_api_key" in msg or "401" in msg:
                st.error("Invalid or missing API key. Add **GROQ_API_KEY** or **OPENAI_API_KEY** in Secrets.")
            else:
                st.error(f"Oops — {e}")

st.markdown("---")
with st.expander("Quick tools"):
    sku = st.text_input("SKU for price lookup", key="sku_price", value="SKU123")
    store = st.text_input("Store ID", key="store_id", value="RTP-001")
    sku_inv = st.text_input("SKU for inventory", key="sku_inv", value="SKU456")
    issue = st.text_input("Issue Summary", key="issue_sum", value="POS freeze during payment")
    notes = st.text_area("Notes", value="Run python ingest.py after editing the markdown files in knowledge_base/ to rebuild the vector store.\nSet GROQ_API_KEY (preferred) or OPENAI_API_KEY in Secrets.")
    st.caption("This demo uses a small local vector DB; push markdown into `knowledge_base/` and redeploy.")
