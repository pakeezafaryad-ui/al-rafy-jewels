"""Optional RAG index builder. Run locally after installing requirements.

Usage:
    python -m rag.ingest

This builds a local FAISS index from Markdown files in data/knowledge_base.
The starter Streamlit app uses a lightweight keyword fallback so it can still
run if embedding dependencies or model downloads are unavailable.
"""
from pathlib import Path
import pickle

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "data" / "knowledge_base"
INDEX_DIR = ROOT / "rag" / "index"

def main():
    try:
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise SystemExit(f"Install requirements first: {exc}")

    chunks, metadata = [], []
    for path in KNOWLEDGE.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for paragraph in paragraphs:
            chunks.append(paragraph)
            metadata.append({"source": path.name, "text": paragraph})
    if not chunks:
        raise SystemExit("No knowledge documents found.")

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    vectors = model.encode(chunks, normalize_embeddings=True)
    vectors = np.asarray(vectors, dtype="float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_DIR / "knowledge.faiss"))
    with open(INDEX_DIR / "metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)
    print(f"Indexed {len(chunks)} knowledge chunks.")

if __name__ == "__main__":
    main()
