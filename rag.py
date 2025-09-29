
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
        docs = retriever.get_relevant_documents(query)
        answer = doc_chain.invoke({"question": query, "context": docs})
        return answer

    return run
