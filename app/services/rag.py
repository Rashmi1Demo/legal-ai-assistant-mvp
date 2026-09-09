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


def retrieve_top_k(query: str, top_k: int = 2, minimum_score: float = 0.0):
    docs = load_documents()
    if not docs or not query.strip():
        return []

    corpus = [d["text"] for d in docs] + [query]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus)
    similarities = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    ranked_indices = similarities.argsort()[::-1]
    results = []
    for index in ranked_indices[:max(top_k, 1)]:
        score = float(similarities[index])
        if score < minimum_score:
            continue
        results.append({
            "name": docs[int(index)]["name"],
            "text": docs[int(index)]["text"],
            "score": score,
        })
    return results


def retrieve(query: str):
    results = retrieve_top_k(query, top_k=1)
    if not results:
        return {"name": "No Knowledge Base", "text": "", "score": 0.0}
    return results[0]
