# rag.py — RAG chain with automatic fallback when OpenAI fails
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

SYSTEM = """
You are a Retail POS assistant. Answer succinctly.
Cite source filenames in brackets like [pos-overview.md].
If a tool call would help, suggest it explicitly.
"""

def _fallback_answer(query: str, docs: List) -> str:
    """Answer purely from retrieved docs when LLM is unavailable (401/429)."""
    if not docs:
        return "I couldn’t find anything in the knowledge base for that yet."
    pieces, seen = [], set()
    for d in docs[:4]:
        text = (d.page_content or "").strip()
        name = (d.metadata.get("source") or d.metadata.get("file_path") or "kb.md").split("/")[-1]
        if text:
            pieces.append(f"**From {name}:**\n{text}")
            seen.add(name)
    cites = " ".join(f"[{n}]" for n in seen)
    return f"**Retrieved answer (fallback, no LLM):**\n\n" + "\n\n".join(pieces) + ("\n\n" + cites if cites else "")

def make_chain(db_dir="vector_store"):
    embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vs = Chroma(persist_directory=db_dir, embedding_function=embed)
    retriever = vs.as_retriever(search_kwargs={"k": 4})

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM),
        ("human", "Question: {question}\nContext: {context}"),
    ])
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    doc_chain = create_stuff_documents_chain(llm, prompt)

    def run(query: str):
        # Newer API: invoke()
        docs = retriever.invoke(query)
        try:
            return doc_chain.invoke({"question": query, "context": docs})
        except Exception:
            # 401 invalid key, 429 quota, etc.
            return _fallback_answer(query, docs)

    return run
