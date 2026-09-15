"""
evaluation.py - Benchmark Test Set Evaluator for KrishiQuery AI
Part of KrishiQuery AI (AGR-25 Farm Advisory Query Rewriter)
"""

from typing import Dict, List, Any
from retriever import AgriculturalRetriever
from query_rewriter import QueryRewriter


TEST_QUERIES = [
    "tomato leaf curling what do",
    "rice leaves yellow",
    "cotton pest on leaves",
    "chilli leaves getting small",
    "maize leaves yellow",
    "plant has white insects",
    "what fertilizer for rice",
    "groundnut leaves turning brown and drying"
]


def run_evaluation(retriever: AgriculturalRetriever = None, rewriter: QueryRewriter = None) -> Dict[str, Any]:
    """
    Evaluates the 8 benchmark farmer questions dynamically.
    For each question, computes:
    - Original retrieval average score (top 3)
    - Rewritten retrieval average score (top 3)
    - Improvement percentage

    Also computes macro-averages and overall improvement.
    """
    if retriever is None:
        retriever = AgriculturalRetriever()
    if rewriter is None:
        rewriter = QueryRewriter()

    eval_rows: List[Dict[str, Any]] = []
    total_original_score = 0.0
    total_rewritten_score = 0.0

    for query in TEST_QUERIES:
        rewrite_result = rewriter.rewrite(query)
        rewritten_query = rewrite_result.get("optimized_query", query)
        method = rewrite_result.get("method", "Fallback Rewriting")

        comparison = retriever.compare(query, rewritten_query, top_k=3)

        orig_avg = comparison["original_average"]
        rewr_avg = comparison["rewritten_average"]
        improvement = comparison["improvement_percent"]

        total_original_score += orig_avg
        total_rewritten_score += rewr_avg

        eval_rows.append({
            "test_query": query,
            "rewritten_query": rewritten_query,
            "method": method,
            "original_score": orig_avg,
            "rewritten_score": rewr_avg,
            "improvement_percent": improvement,
            "top_original_title": comparison["original_results"][0]["title"] if comparison["original_results"] else "None",
            "top_rewritten_title": comparison["rewritten_results"][0]["title"] if comparison["rewritten_results"] else "None"
        })

    num_queries = len(TEST_QUERIES)
    mean_original = round(total_original_score / num_queries, 3)
    mean_rewritten = round(total_rewritten_score / num_queries, 3)

    if mean_original > 0:
        overall_improvement = round(((mean_rewritten - mean_original) / mean_original) * 100, 1)
    else:
        overall_improvement = 100.0 if mean_rewritten > 0 else 0.0

    return {
        "results": eval_rows,
        "summary": {
            "total_queries": num_queries,
            "mean_original_score": mean_original,
            "mean_rewritten_score": mean_rewritten,
            "overall_improvement_percent": overall_improvement
        }
    }


if __name__ == "__main__":
    import pprint
    res = run_evaluation()
    print("=== KRISHIQUERY AI BENCHMARK RESULTS ===")
    for row in res["results"]:
        print(f"Query: {row['test_query']} | Orig: {row['original_score']} | Rewr: {row['rewritten_score']} | Imprv: +{row['improvement_percent']}%")
    print("\nSummary:", res["summary"])
