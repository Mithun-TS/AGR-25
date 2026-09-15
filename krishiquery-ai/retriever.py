"""
retriever.py - Lightweight TF-IDF + Cosine Similarity Agricultural Document Retriever
Part of KrishiQuery AI (AGR-25 Farm Advisory Query Rewriter)
"""

import os
import json
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class AgriculturalRetriever:
    """
    Retrieves relevant agricultural advisory documents using TF-IDF and Cosine Similarity.
    """

    def __init__(self, data_path: str = None):
        if data_path is None:
            # Default to relative data directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(current_dir, "data", "agriculture.json")

        self.data_path = data_path
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer: TfidfVectorizer = None
        self.tfidf_matrix = None
        self.load_and_index()

    def load_and_index(self):
        """Loads JSON document corpus and builds TF-IDF index."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Knowledge base not found at: {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        # Build corpus representation: give higher weight to crop and title for sharper matching
        corpus = [
            f"{doc.get('crop', '')} {doc.get('title', '')} {doc.get('title', '')} {doc.get('content', '')}"
            for doc in self.documents
        ]

        # Use 1-2 ngrams and sublinear term frequency for robust retrieval
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves the top_k most similar documents for a given query string.
        """
        if not query or not query.strip():
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        # Sort indices by similarity descending
        ranked_indices = similarities.argsort()[::-1]

        results = []
        for idx in ranked_indices[:top_k]:
            doc = self.documents[idx]
            score = float(similarities[idx])
            # Return realistic snippet or full content
            content = doc.get("content", "")
            snippet = content[:160] + "..." if len(content) > 160 else content
            results.append({
                "id": doc.get("id"),
                "crop": doc.get("crop", "").capitalize(),
                "title": doc.get("title", ""),
                "content": content,
                "snippet": snippet,
                "score": round(score, 3)
            })

        return results

    def compare(self, original_query: str, rewritten_query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Executes Retrieval A (original) and Retrieval B (rewritten),
        computes top_k documents for each, and calculates average scores and improvement %.
        """
        original_results = self.retrieve(original_query, top_k=top_k)
        rewritten_results = self.retrieve(rewritten_query, top_k=top_k)

        orig_scores = [r["score"] for r in original_results] if original_results else [0.0]
        rewr_scores = [r["score"] for r in rewritten_results] if rewritten_results else [0.0]

        orig_avg = round(sum(orig_scores) / max(len(orig_scores), 1), 3)
        rewr_avg = round(sum(rewr_scores) / max(len(rewr_scores), 1), 3)

        if orig_avg > 0:
            improvement = round(((rewr_avg - orig_avg) / orig_avg) * 100, 1)
        else:
            improvement = 100.0 if rewr_avg > 0 else 0.0

        return {
            "original_query": original_query,
            "rewritten_query": rewritten_query,
            "original_results": original_results,
            "rewritten_results": rewritten_results,
            "original_average": orig_avg,
            "rewritten_average": rewr_avg,
            "improvement_percent": improvement,
            "disclaimer": "Similarity improvement is a lightweight retrieval indicator, not a measure of factual correctness."
        }
