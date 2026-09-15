"""
test_advisory.py - Automated Verification of Open-Domain Agricultural Advisory Flow
Tests the 5 required unseen farmer queries:
1. mango fruit black spot
2. banana leaves getting black
3. onion bulb rot
4. cotton boll worms
5. chilli fruit falling
"""

import sys
import json
import urllib.request
from query_rewriter import QueryRewriter
from web_search import AgriculturalSearchEngine

BASE_URL = "http://127.0.0.1:5000"

TEST_CASES = [
    {
        "query": "mango fruit black spot",
        "expected_crop": "Mango",
        "expected_part": "Fruit",
        "expected_problem": "Black spot",
        "must_not_contain": ["tomato", "rice", "cotton", "tikka", "khaira"]
    },
    {
        "query": "banana leaves getting black",
        "expected_crop": "Banana",
        "expected_part": "Leaves",
        "expected_problem": "Blackening / getting black",
        "must_not_contain": ["tomato", "cotton", "khaira", "whitefly"]
    },
    {
        "query": "onion bulb rot",
        "expected_crop": "Onion",
        "expected_part": "Bulb / Root",
        "expected_problem": "Bulb rot",
        "must_not_contain": ["tomato", "cotton", "rice", "tikka"]
    },
    {
        "query": "cotton boll worms",
        "expected_crop": "Cotton",
        "expected_part": "Boll",
        "expected_problem": "Bollworm infestation",
        "must_not_contain": ["tomato", "rice", "onion", "banana"]
    },
    {
        "query": "chilli fruit falling",
        "expected_crop": "Chilli",
        "expected_part": "Fruit",
        "expected_problem": "Fruit drop / falling",
        "must_not_contain": ["mango", "onion", "rice"]
    }
]

def run_tests():
    print("=== Running Open-Domain Advisory Verification Suite ===\n")
    rewriter = QueryRewriter()
    search_engine = AgriculturalSearchEngine()

    for idx, tc in enumerate(TEST_CASES, 1):
        q = tc["query"]
        print(f"[{idx}/5] Testing Query: '{q}'")

        # 1. Test Query Rewriter Entity Extraction
        res = rewriter.rewrite(q)
        crop = res.get("crop")
        part = res.get("plant_part")
        problem = res.get("problem")
        opt_query = res.get("optimized_query", "")

        assert crop == tc["expected_crop"], f"Crop mismatch: expected {tc['expected_crop']}, got {crop}"
        assert part == tc["expected_part"], f"Plant part mismatch: expected {tc['expected_part']}, got {part}"
        assert tc["expected_problem"] in problem, f"Problem mismatch: expected {tc['expected_problem']}, got {problem}"

        # Ensure no hallucinated / forced cross-crop disease terms
        for forbidden in tc["must_not_contain"]:
            assert forbidden not in opt_query.lower(), f"Premature/invented disease term '{forbidden}' found in rewritten query: {opt_query}"

        print(f"  [PASS] Extracted: Crop='{crop}', Part='{part}', Problem='{problem}'")
        print(f"  [PASS] Optimized Query: \"{opt_query}\"")

        # 2. Test Live Web Search & Guidance
        sources = search_engine.search_web(opt_query, crop=crop, max_results=3)
        assert len(sources) > 0, f"Expected web sources for {q}"
        guidance = search_engine.generate_guidance(res, sources)
        assert len(guidance) > 50, f"Expected guidance text for {q}"
        assert "Safety Caution" in guidance, f"Expected safety caution in guidance for {q}"
        print(f"  [PASS] Sources retrieved: {len(sources)} | Guidance synthesized ({len(guidance)} chars)")

        # 3. Test HTTP /api/advisory API endpoint
        req = urllib.request.Request(
            f"{BASE_URL}/api/advisory",
            data=json.dumps({"query": q}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            assert resp.status == 200, f"HTTP {resp.status} on /api/advisory for {q}"
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "success"
            assert data["understanding"]["crop"] == tc["expected_crop"]
            assert data["understanding"]["plant_part"] == tc["expected_part"]
            print(f"  [PASS] API /api/advisory HTTP 200 OK")

        print("-" * 60)

    print("\n*** ALL 5 UNSEEN ADVISORY QUERIES PASSED WITH ZERO CROSS-CROP HALLUCINATIONS! ***\n")

if __name__ == "__main__":
    run_tests()
