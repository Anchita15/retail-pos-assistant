# ingest.py — builds a guaranteed non-empty Chroma index
import pathlib
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

KB_DIR = "knowledge_base"
DB_DIR = "vector_store"

STARTER = """# Starter Notes (Generated)
This was auto-created because no markdown files were found or they were empty.

## POS Basics
- Hardware: terminals, scanners, receipt printers, cash drawers, card readers.
- Software: transactions, pricing/tax, promotions, inventory, returns, reporting.
- Payments: processor/gateway, tokenization, offline queue.
- Data: item/price/offer services, loyalty, audit logs, reconciliation.
- Cloud: sync APIs, monitoring, backups/DR.
"""

def _nonempty_md_files(kb: pathlib.Path) -> list[pathlib.Path]:
    files = [p for p in kb.glob("**/*.md") if p.is_file()]
    keep = []
    for p in files:
        try:
            if p.read_text(encoding="utf-8").strip():
                keep.append(p)
        except Exception:
            pass
    return keep

def ensure_kb_has_content() -> list[str]:
    kb = pathlib.Path(KB_DIR)
    kb.mkdir(parents=True, exist_ok=True)
    keep = _nonempty_md_files(kb)
    if not keep:
        starter = kb / "starter.md"
        starter.write_text(STARTER, encoding="utf-8")
        keep = [starter]
    return [str(p) for p in keep]

def build_store(src_dir=KB_DIR, db_dir=DB_DIR):
    paths = ensure_kb_has_content()
    print("KB files to ingest:", paths)

    docs = []
    for f in paths:
        docs += TextLoader(f, encoding="utf-8").load()
    print("Loaded docs:", len(docs))

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    if not chunks:
        # create a minimal starter then re-split
        starter = pathlib.Path(src_dir) / "starter.md"
        if not starter.exists():
            starter.write_text(STARTER, encoding="utf-8")
        docs = TextLoader(str(starter), encoding="utf-8").load()
        chunks = splitter.split_documents(docs)

    embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Chroma.from_documents(chunks, embedding=embed, persist_directory=db_dir)
    print(f"Indexed {len(chunks)} chunks → {db_dir}")

if __name__ == "__main__":
    build_store()
