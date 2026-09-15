"""
test_e2e.py - Complete End-to-End Test Suite for Agri Advisory
Validates HTTP endpoints, query rewriting, TF-IDF dual retrieval, and benchmark evaluation.
"""

import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(name, method="GET", path="/", data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            content = response.read().decode("utf-8")
            return status, content
    except Exception as e:
        print(f"FAILED {name}: {e}")
        sys.exit(1)

print("--- Running Agri Advisory Verification Suite ---")

# 1. Test Index Page
status, content = test_endpoint("Home Page", path="/")
assert status == 200, f"Expected 200, got {status}"
assert "Agri Advisory" in content, "Brand title not in index page"
assert "tomato leaf curling what do" in content, "Example query missing"
print("[PASS] Index page loaded with 200 OK and valid markup.")

# 2. Test Examples Endpoint
status, content = test_endpoint("Examples API", path="/api/examples")
data = json.loads(content)
assert "examples" in data and len(data["examples"]) >= 7, f"Examples count incorrect: {len(data.get('examples', []))}"
print(f"[PASS] Examples endpoint returned {len(data['examples'])} example queries.")

# 3. Test Rewrite & Search with 3 distinct queries
test_queries = [
    "tomato leaf curling what do",
    "rice leaves yellow",
    "cotton pest on leaves"
]

for q in test_queries:
    status, content = test_endpoint(f"Rewrite & Search: '{q}'", method="POST", path="/api/rewrite-and-search", data={"query": q})
    res = json.loads(content)
    assert res["status"] == "success", f"Search failed for {q}"
    assert len(res["original_results"]) == 3, f"Expected 3 original results for {q}"
    assert len(res["rewritten_results"]) == 3, f"Expected 3 rewritten results for {q}"
    assert res["rewritten_average"] >= res["original_average"], f"Expected rewritten score >= original for {q}"
    print(f"[PASS] Query '{q}': Orig Avg={res['original_average']} -> Rewr Avg={res['rewritten_average']} (+{res['improvement_percent']}%) | Crop={res['analysis']['crop']}")

# 4. Test Benchmark Evaluation Endpoint
status, content = test_endpoint("Benchmark Evaluation API", path="/api/evaluate")
eval_data = json.loads(content)["data"]
results = eval_data["results"]
summary = eval_data["summary"]

assert len(results) == 8, f"Expected 8 benchmark results, got {len(results)}"
assert summary["overall_improvement_percent"] > 50, f"Expected significant improvement, got {summary['overall_improvement_percent']}%"
print(f"[PASS] Benchmark Evaluation: 8 queries evaluated | Overall Improvement: +{summary['overall_improvement_percent']}%")

print("\n*** ALL TESTS PASSED SUCCESSFULLY! ***")
