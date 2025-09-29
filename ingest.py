# ingest.py - robust build: creates a starter note if KB is empty
import glob, os, pathlib
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

KB_DIR = "knowledge_base"
DB_DIR = "vector_store"

STARTER = """# Starter Notes (Generated)
This was auto-created because no markdown files were found or they were empty.

## POS Basics
- POS client, pricing/tax, promotions/loyalty, inventory, payments, data stores.
- Event-driven integrations; idempotent endpoints; retries with backoff."""
 
def ensure_kb_has_content() -> list[str]:
    kb = pathlib.Path(KB_DIR)
    kb.mkdir(parents=True, exist_ok=True)
    files = [p for p in kb.glob("**/*.md") if p.is_file()]
    nonempty = []
    for p in files:
        try:
            if p.read_text(encoding="utf-8").strip():
                nonempty.append(p)
        except Exception:
            pass
    if not nonempty:
        starter = kb / "starter.md"
        starter.write_text(STARTER, encoding="utf-8")
        nonempty = [starter]
    return [str(p) for p in nonempty]

def build_store(src_dir=KB_DIR, db_dir=DB_DIR):
    paths = ensure_kb_has_content()
    print("KB files to ingest:", paths)
    docs = []
    for f in paths:
        docs += TextLoader(f, encoding="utf-8").load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    print("Total chunks:", len(chunks))
    if not chunks:
        # safety guard (shouldn’t happen with starter)
        starter = pathlib.Path(src_dir) / "starter.md"
        starter.write_text(STARTER, encoding="utf-8")
        docs = TextLoader(str(starter), encoding="utf-8").load()
        chunks = splitter.split_documents(docs)

    embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    Chroma.from_documents(chunks, embedding=embed, persist_directory=db_dir)
    print(f"Indexed {len(chunks)} chunks → {db_dir}")

if __name__ == "__main__":
    build_store()
