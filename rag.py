# rag.py - retrieval + LLM chain
import os
from typing import List
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

# Choose model provider: prefer GROQ (free), fallback to OpenAI
def _llm():
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        from langchain_groq import ChatGroq
        # Fast + inexpensive:
        return ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, max_tokens=512)
    from langchain_openai import ChatOpenAI
    # Use gpt-4o-mini for cost, or override via OPENAI_MODEL in secrets
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0.1, max_tokens=512)

SYSTEM = """You are a Retail POS assistant. 
Answer succinctly. If context lacks an answer, say you don’t know and suggest related topics to click in the app.
Use bullet points where helpful."""

def _retriever(db_dir: str):
    embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vs = Chroma(persist_directory=db_dir, embedding_function=embed)
    return vs.as_retriever(search_kwargs={"k": 4})

def make_chain(db_dir: str):
    retriever = _retriever(db_dir)
    llm = _llm()

    prompt = ChatPromptTemplate.from_template(
        "{system}\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )

    def fetch_context(q: str) -> List[Document]:
        # .invoke() is the new API; .get_relevant_documents() still works
        try:
            return retriever.invoke(q)  # returns List[Document]
        except Exception:
            return []

    def run(query: str) -> str:
        docs = fetch_context(query)
        ctx = "\n\n".join(d.page_content[:1200] for d in docs) if docs else "N/A"
        chain = prompt | llm | RunnableLambda(lambda m: m.content if hasattr(m, "content") else str(m))
        reply = chain.invoke({"system": SYSTEM, "context": ctx, "question": query})
        # Friendly fallback if nothing was found AND reply is generic
        if (not docs) and ("I don’t know" in reply or "I don't know" in reply or reply.strip() == ""):
            return "I couldn’t find anything in the knowledge base for that yet."
        return reply

    return run
