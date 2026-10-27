from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"

def load_documents():
    docs = []
    if KNOWLEDGE_DIR.exists():
        for path in KNOWLEDGE_DIR.glob("*.md"):
            try:
                text = path.read_text(encoding="utf-8").strip()
                if text:
                    docs.append({"source": path.name, "text": text})
            except OSError:
                continue
    return docs

def answer_with_rag(question):
    """Lightweight keyword retrieval fallback. Run rag/ingest.py for FAISS indexing experiments."""
    docs = load_documents()
    if not docs:
        return "The store knowledge base is empty. Please contact Al Rafy Jewels for confirmation."
    terms = {w.lower().strip(".,?!:;") for w in question.split() if len(w) > 2}
    scored = []
    for doc in docs:
        content_terms = set(doc["text"].lower().split())
        score = len(terms & content_terms)
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    best = [(score, doc) for score, doc in scored if score > 0][:2]
    if not best:
        return "I couldn't find a reliable answer in the current store documents. Please contact the store for confirmation."
    return "\n\n".join(f"**Source: {doc['source']}**\n{doc['text'][:1800]}" for _, doc in best)
