# ingest.py - build vector DB from markdown
import pathlib
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

KB_DIR = "knowledge_base"
DB_DIR = "vector_store"

STARTER = """# POS basics (starter)
This file was auto-created because no non-empty markdown was found.

## Key POS components
- Hardware: terminals, scanners, receipt printers, drawers, payment readers (NFC/chip/swipe)
- Software: sales/returns, inventory, loyalty, tax, promotions, reporting
- Payments: gateway, tokenization, PCI, offline queues
- Ops: price checks, coupons, voids, EOD, reconciliation
"""

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
    docs = []
    for f in paths:
        docs += TextLoader(f, encoding="utf-8").load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    if not chunks:
        # Safety net: put one chunk so Chroma never gets []
        from langchain_core.documents import Document
        chunks = [Document(page_content="Fallback chunk: POS overview starter.")]
    embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    Chroma.from_documents(chunks, embedding=embed, persist_directory=db_dir)
    print(f"Indexed {len(chunks)} chunks → {db_dir}")

if __name__ == "__main__":
    build_store()
