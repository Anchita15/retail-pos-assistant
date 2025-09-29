# ingest.py - build a local vector store from your original markdown notes
import glob, os
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

def build_store(src_dir="knowledge_base", db_dir="vector_store"):
    files = glob.glob(os.path.join(src_dir, "**/*.md"), recursive=True)
    docs = []
    for f in files:
        docs += TextLoader(f, encoding="utf-8").load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    Chroma.from_documents(chunks, embedding=embed, persist_directory=db_dir)
    print(f"Indexed {len(chunks)} chunks → {db_dir}")

if __name__ == "__main__":
    build_store()
