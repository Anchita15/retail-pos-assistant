# app.py - Streamlit UI for the Retail POS LLM Assistant
import streamlit as st
from rag import make_chain
from agents import price_lookup, inventory_check, issue_ticket

st.set_page_config(page_title="Retail POS LLM Assistant", page_icon="🧾")
st.title("Retail POS LLM Assistant 🧾")
st.caption("RAG + simple agentic tools for retail POS scenarios")

if "chain" not in st.session_state:
    st.session_state.chain = make_chain()

with st.form("qa_form", clear_on_submit=False):
    q = st.text_input("Ask about POS ops, coupons, troubleshooting, etc.")
    submitted = st.form_submit_button("Answer")
    if submitted and q:
        answer = st.session_state.chain(q)
        st.markdown(answer)

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
    "- Run `python ingest.py` after editing the markdown files in `knowledge_base/` to rebuild the vector store.  \n"
    "- Set `OPENAI_API_KEY` in `.streamlit/secrets.toml` or as an environment variable.  \n"
)
