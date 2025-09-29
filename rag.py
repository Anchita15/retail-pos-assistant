# rag.py — RAG chain with LLM + robust KB-only fallback
from typing import List
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

try:
    from langchain_openai import ChatOpenAI
    _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False

SYSTEM = (
    "You are a Retail POS assistant. Be succinct. "
    "Cite source filenames in brackets like [pos-overview.md]."
)

def _fallback_answer(query: str, docs: List) -> str:
    if not docs:
        return "I couldn’t find anything in the knowledge base for that yet."
    seen = set()
    bullets = []
    for d in docs[:4]:
        name = (d.metadata.get("source") or d.metadata.get("file_path") or "kb.md").split("/")[-1]
        seen.add(name)
        bullets.append(f"- **{name}**: {d.page_content.strip()[:350]}…")
    cites = " ".join(f"[{s}]" for s in seen)
    return f"**KB result (no LLM)**\n\n" + "\n".join(bullets) + (f"\n\n{cites}" if cites else "")

def make_chain(db_dir="vector_store"):
    embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vs = Chroma(persist_directory=db_dir, embedding_function=embed)
    retriever = vs.as_retriever(search_kwargs={"k": 4})

    def run(query: str):
        docs = retriever.invoke(query)
        if _HAS_OPENAI:
            try:
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
                prompt = ChatPromptTemplate.from_messages([
                    ("system", SYSTEM),
                    ("human", "Question: {question}\nContext: {context}")
                ])
                chain = create_stuff_documents_chain(llm, prompt)
                return chain.invoke({"question": query, "context": docs})
            except Exception:
                return _fallback_answer(query, docs)
        else:
            return _fallback_answer(query, docs)

    return run
