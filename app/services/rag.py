from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_DIR = Path(__file__).resolve().parents[2] / "knowledge_base"

def load_documents():
    docs = []
    for path in sorted(KB_DIR.glob("*.txt")):
        docs.append({
            "name": path.stem,
            "text": path.read_text(encoding="utf-8")
        })
    return docs

def retrieve(query: str):
    docs = load_documents()
    if not docs:
        return {"name": "No Knowledge Base", "text": "", "score": 0.0}

    corpus = [d["text"] for d in docs] + [query]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus)
    similarities = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    best_index = int(similarities.argmax())

    return {
        "name": docs[best_index]["name"],
        "text": docs[best_index]["text"],
        "score": float(similarities[best_index])
    }
