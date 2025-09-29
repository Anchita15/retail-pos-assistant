from typing import Callable
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DB_COLLECTION = "pos_kb"

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a retail POS assistant. Answer clearly and cite relevant KB snippets when helpful."),
        ("human",
         "Question: {question}\n\nUse this context:\n{context}")
    ]
)

def _retriever(db_dir: str):
    embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vs = Chroma(
        persist_directory=db_dir,
        embedding_function=embed,
        collection_name=DB_COLLECTION,
    )
    return vs.as_retriever(search_kwargs={"k": 4})

def make_chain(db_dir: str) -> Callable[[str], str]:
    retriever = _retriever(db_dir)

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )

    def run(query: str) -> str:
        docs = retriever.get_relevant_documents(query)
        context = "\n\n".join([f"[{i+1}] {d.page_content}" for i, d in enumerate(docs)])
        msg = PROMPT.format_messages(question=query, context=context)
        resp = llm.invoke(msg)
        return resp.content

    return run
