"""
app.py - Flask Web Application for Agri Advisory
Part of Agri Advisory (AGR-25 Farm Advisory Query Rewriter)
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from retriever import AgriculturalRetriever
from query_rewriter import QueryRewriter
from evaluation import run_evaluation, TEST_QUERIES
from web_search import AgriculturalSearchEngine

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")

# Initialize retriever, query rewriter, and web search engine once at startup
retriever = AgriculturalRetriever()
rewriter = QueryRewriter()
search_engine = AgriculturalSearchEngine()

EXAMPLE_QUERIES = [
    "mango fruit black spot",
    "banana leaves getting black",
    "onion bulb rot",
    "cotton boll worms",
    "chilli fruit falling",
    "tomato leaf curling what do",
    "rice leaves yellow",
    "what fertilizer for rice"
]


@app.route("/")
def index():
    """Renders main dashboard interface."""
    return render_template("index.html", examples=EXAMPLE_QUERIES)


@app.route("/api/examples", methods=["GET"])
def get_examples():
    """Returns preset example queries."""
    return jsonify({"examples": EXAMPLE_QUERIES})


@app.route("/api/advisory", methods=["POST"])
def get_advisory():
    """
    Open-Domain Advisory Endpoint:
    Farmer Question -> AI Query Understanding -> Optimized Search Query -> Web Sources -> Concise Guidance.
    """
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({
            "status": "error",
            "message": "Please enter a valid farming question."
        }), 400

    # 1. AI Understanding & Rewriting
    rewrite_meta = rewriter.rewrite(query)
    rewritten_query = rewrite_meta.get("optimized_query", query)
    method = rewrite_meta.get("method", "Fallback Rewriting")

    understanding = {
        "crop": rewrite_meta.get("crop", "Not specified"),
        "plant_part": rewrite_meta.get("plant_part", "Not specified"),
        "problem": rewrite_meta.get("problem", "Not specified"),
        "intent": rewrite_meta.get("intent", "Not specified")
    }

    # 2. Live Web Search
    sources = search_engine.search_web(rewritten_query, crop=understanding["crop"], max_results=3)

    # 3. Local TF-IDF matches (if relevant crop exists in local dataset)
    local_matches = retriever.retrieve(rewritten_query, top_k=2)

    # 4. Generate Safe, Concise Guidance
    guidance = search_engine.generate_guidance(understanding, sources)

    return jsonify({
        "status": "success",
        "original_query": query,
        "understanding": understanding,
        "optimized_query": rewritten_query,
        "method": method,
        "sources": sources,
        "guidance": guidance,
        "local_matches": local_matches
    })


@app.route("/api/rewrite-and-search", methods=["POST"])
def rewrite_and_search():
    """
    Core API endpoint:
    Takes raw farmer query -> parses & rewrites -> performs dual retrieval -> computes improvement.
    """
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({
            "status": "error",
            "message": "Please enter a valid query or select an example."
        }), 400

    # 1. Rewrite query (AI or Fallback)
    rewrite_meta = rewriter.rewrite(query)
    rewritten_query = rewrite_meta.get("optimized_query", query)
    method = rewrite_meta.get("method", "Fallback Rewriting")

    # 2. Dual Retrieval comparison
    comparison = retriever.compare(query, rewritten_query, top_k=3)

    return jsonify({
        "status": "success",
        "original_query": query,
        "analysis": {
            "crop": rewrite_meta.get("crop", "Not specified"),
            "plant_part": rewrite_meta.get("plant_part", "Not specified"),
            "problem": rewrite_meta.get("problem", "Not specified"),
            "intent": rewrite_meta.get("intent", "Not specified"),
            "location": rewrite_meta.get("location", "Not specified"),
            "season": rewrite_meta.get("season", "Not specified"),
            "method": method
        },
        "rewritten_query": rewritten_query,
        "method": method,
        "original_results": comparison["original_results"],
        "rewritten_results": comparison["rewritten_results"],
        "original_average": comparison["original_average"],
        "rewritten_average": comparison["rewritten_average"],
        "improvement_percent": comparison["improvement_percent"],
        "disclaimer": comparison["disclaimer"]
    })


@app.route("/api/evaluate", methods=["GET"])
def evaluate():
    """
    Runs dynamic evaluation across the 8 benchmark queries.
    """
    try:
        eval_data = run_evaluation(retriever=retriever, rewriter=rewriter)
        return jsonify({
            "status": "success",
            "data": eval_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "True").lower() in ("true", "1")
    print(f"[Agri Advisory] Starting at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
