/**
 * Agri Advisory - Client Application Logic (Frontend for Vercel)
 * Part of AGR-25 Farm Advisory Query Rewriter
 * Upgraded to support Open-Domain Advisory, Plant Parts, and Web Sources.
 */

// Set your deployed Render backend URL here (e.g. "https://agr-25.onrender.com")
const API_URL = "RENDER_BACKEND_URL";

function getApiUrl(path) {
  if (!API_URL || API_URL === "RENDER_BACKEND_URL") {
    return path;
  }
  return `${API_URL.replace(/\/+$/, "")}${path}`;
}

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const searchForm = document.getElementById("searchForm");
  const queryInput = document.getElementById("queryInput");
  const askAiBtn = document.getElementById("askAiBtn");
  const searchBtn = document.getElementById("searchBtn");
  const clearBtn = document.getElementById("clearBtn");
  const tryExampleBtn = document.getElementById("tryExampleBtn");
  const exampleChips = document.querySelectorAll(".chip");
  const copyQueryBtn = document.getElementById("copyQueryBtn");

  const loadingState = document.getElementById("loadingState");
  const resultsContainer = document.getElementById("resultsContainer");

  // Analysis Elements
  const methodBadge = document.getElementById("methodBadge");
  const methodText = document.getElementById("methodText");
  const analysisCrop = document.getElementById("analysisCrop");
  const analysisPlantPart = document.getElementById("analysisPlantPart");
  const analysisProblem = document.getElementById("analysisProblem");
  const analysisIntent = document.getElementById("analysisIntent");
  const rewrittenQueryText = document.getElementById("rewrittenQueryText");

  // Advisory Elements
  const sourcesGrid = document.getElementById("sourcesGrid");
  const guidanceContent = document.getElementById("guidanceContent");

  // Comparison Elements
  const comparisonSection = document.getElementById("comparisonSection");
  const origQueryPreview = document.getElementById("origQueryPreview");
  const rewrQueryPreview = document.getElementById("rewrQueryPreview");
  const origAvgScore = document.getElementById("origAvgScore");
  const rewrAvgScore = document.getElementById("rewrAvgScore");
  const origResultsList = document.getElementById("origResultsList");
  const rewrResultsList = document.getElementById("rewrResultsList");

  // Improvement Elements
  const improvementValue = document.getElementById("improvementValue");
  const barOrig = document.getElementById("barOrig");
  const barRewr = document.getElementById("barRewr");
  const barOrigText = document.getElementById("barOrigText");
  const barRewrText = document.getElementById("barRewrText");
  const disclaimerText = document.getElementById("disclaimerText");

  // Evaluation Elements
  const evalBtn = document.getElementById("evalBtn");
  const evalLoading = document.getElementById("evalLoading");
  const evalTableWrapper = document.getElementById("evalTableWrapper");
  const evalTableBody = document.getElementById("evalTableBody");
  const evalMeanOrig = document.getElementById("evalMeanOrig");
  const evalMeanRewr = document.getElementById("evalMeanRewr");
  const evalOverallImp = document.getElementById("evalOverallImp");

  // Example questions list
  const presetExamples = [
    "mango fruit black spot",
    "banana leaves getting black",
    "onion bulb rot",
    "cotton boll worms",
    "chilli fruit falling",
    "tomato leaf curling what do",
    "rice leaves yellow",
    "what fertilizer for rice"
  ];
  let currentExampleIdx = 0;

  // --- Handlers ---

  // Handle Form Submit (Ask AI Advisory)
  searchForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;
    await executeAdvisoryAndRetrieval(query);
  });

  // Compare Retrieval Button click
  if (searchBtn) {
    searchBtn.addEventListener("click", async () => {
      const query = queryInput.value.trim();
      if (!query) return;
      await executeAdvisoryAndRetrieval(query);
      if (comparisonSection) {
        comparisonSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }

  // Clear button
  clearBtn.addEventListener("click", () => {
    queryInput.value = "";
    queryInput.focus();
  });

  // Try Example Button
  tryExampleBtn.addEventListener("click", () => {
    currentExampleIdx = (currentExampleIdx + 1) % presetExamples.length;
    const chosen = presetExamples[currentExampleIdx];
    queryInput.value = chosen;
    executeAdvisoryAndRetrieval(chosen);
  });

  // Example Chips Click
  exampleChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      queryInput.value = q;
      executeAdvisoryAndRetrieval(q);
    });
  });

  // Copy Query Button
  copyQueryBtn.addEventListener("click", () => {
    const text = rewrittenQueryText.textContent.replace(/^"|"$/g, "").trim();
    navigator.clipboard.writeText(text).then(() => {
      const origText = copyQueryBtn.textContent;
      copyQueryBtn.textContent = "Copied!";
      setTimeout(() => {
        copyQueryBtn.textContent = origText;
      }, 1500);
    });
  });

  // Run Evaluation Button
  evalBtn.addEventListener("click", async () => {
    evalLoading.classList.remove("hidden");
    evalTableWrapper.classList.add("hidden");
    evalBtn.disabled = true;

    try {
      const res = await fetch(getApiUrl("/api/evaluate"));
      const data = await res.json();

      if (data.status === "success") {
        renderEvaluationTable(data.data);
      } else {
        alert("Evaluation failed: " + (data.message || "Unknown error"));
      }
    } catch (err) {
      alert("Network error running evaluation: " + err.message);
    } finally {
      evalLoading.classList.add("hidden");
      evalBtn.disabled = false;
    }
  });

  // --- Core Functions ---

  async function executeAdvisoryAndRetrieval(query) {
    // Show loading
    loadingState.classList.remove("hidden");
    resultsContainer.classList.add("hidden");
    if (askAiBtn) askAiBtn.disabled = true;
    if (searchBtn) searchBtn.disabled = true;

    try {
      // Execute both Advisory & Retrieval Comparison concurrently
      const [advisoryRes, retrievalRes] = await Promise.all([
        fetch(getApiUrl("/api/advisory"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query })
        }).then((r) => r.json()),
        fetch(getApiUrl("/api/rewrite-and-search"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query })
        }).then((r) => r.json())
      ]);

      if (advisoryRes.status === "success" && retrievalRes.status === "success") {
        renderResults(advisoryRes, retrievalRes);
      } else {
        alert((advisoryRes.message || retrievalRes.message) || "Error processing request.");
      }
    } catch (err) {
      console.error("API error:", err);
      alert("Failed to communicate with server: " + err.message);
    } finally {
      loadingState.classList.add("hidden");
      resultsContainer.classList.remove("hidden");
      if (askAiBtn) askAiBtn.disabled = false;
      if (searchBtn) searchBtn.disabled = false;
    }
  }

  function renderResults(advisory, retrieval) {
    const understanding = advisory.understanding;
    const method = advisory.method;

    // 1. Method badge
    methodText.textContent = method;
    if (method === "AI Rewriting") {
      methodBadge.className = "badge badge-method badge-ai";
    } else {
      methodBadge.className = "badge badge-method badge-fallback";
    }

    // 2. Entity values
    analysisCrop.textContent = understanding.crop || "Not specified";
    if (analysisPlantPart) {
      analysisPlantPart.textContent = understanding.plant_part || "Not specified";
    }
    analysisProblem.textContent = understanding.problem || "Not specified";
    analysisIntent.textContent = understanding.intent || "Not specified";

    // 3. Rewritten Query
    rewrittenQueryText.textContent = `"${advisory.optimized_query}"`;

    // 4. Render Retrieved Sources
    sourcesGrid.innerHTML = "";
    if (advisory.sources && advisory.sources.length > 0) {
      advisory.sources.forEach((src) => {
        const card = document.createElement("div");
        card.className = "source-card";
        card.innerHTML = `
          <span class="source-badge">${escapeHtml(src.source)}</span>
          <a href="${escapeHtml(src.url)}" target="_blank" rel="noopener" class="source-title-link">
            <span>${escapeHtml(src.title)}</span>
            <span class="source-link-icon">↗</span>
          </a>
          <p class="source-snippet">${escapeHtml(src.snippet)}</p>
        `;
        sourcesGrid.appendChild(card);
      });
    } else {
      sourcesGrid.innerHTML = `<p class="text-muted">No external sources returned; local extension guidelines applied.</p>`;
    }

    // 5. Render Farmer Guidance
    renderGuidance(advisory.guidance);

    // 6. Render Side-by-Side Retrieval Comparison
    origQueryPreview.textContent = `"${retrieval.original_query}"`;
    origAvgScore.textContent = Number(retrieval.original_average).toFixed(3);

    rewrQueryPreview.textContent = `"${retrieval.rewritten_query}"`;
    rewrAvgScore.textContent = Number(retrieval.rewritten_average).toFixed(3);

    origResultsList.innerHTML = "";
    retrieval.original_results.forEach((doc, idx) => {
      origResultsList.appendChild(createResultCard(doc, idx + 1, false));
    });

    rewrResultsList.innerHTML = "";
    retrieval.rewritten_results.forEach((doc, idx) => {
      rewrResultsList.appendChild(createResultCard(doc, idx + 1, true));
    });

    // 7. Improvement Metrics & Bars
    const imprv = retrieval.improvement_percent;
    const sign = imprv >= 0 ? "+" : "";
    improvementValue.textContent = `${sign}${Number(imprv).toFixed(1)}%`;

    barOrigText.textContent = Number(retrieval.original_average).toFixed(3);
    barRewrText.textContent = Number(retrieval.rewritten_average).toFixed(3);

    const maxScore = Math.max(0.40, retrieval.rewritten_average * 1.15);
    const pctOrig = Math.min(100, Math.round((retrieval.original_average / maxScore) * 100));
    const pctRewr = Math.min(100, Math.round((retrieval.rewritten_average / maxScore) * 100));

    barOrig.style.width = `${Math.max(10, pctOrig)}%`;
    barRewr.style.width = `${Math.max(15, pctRewr)}%`;

    if (retrieval.disclaimer) {
      disclaimerText.textContent = retrieval.disclaimer;
    }
  }

  function renderGuidance(text) {
    if (!text) {
      guidanceContent.innerHTML = "<p>No guidance available.</p>";
      return;
    }

    // Format markdown bold **text** to <strong>text</strong>
    const formatted = escapeHtml(text)
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n\n/g, "<br><br>")
      .replace(/\n/g, "<br>");

    guidanceContent.innerHTML = formatted;
  }

  function createResultCard(doc, rank, isRewritten) {
    const card = document.createElement("div");
    card.className = "result-card";

    card.innerHTML = `
      <div class="result-card-top">
        <span class="crop-tag">${escapeHtml(doc.crop)}</span>
        <span class="result-score" title="Cosine Similarity Score">Score: ${Number(doc.score).toFixed(3)}</span>
      </div>
      <h4 class="result-title">#${rank}. ${escapeHtml(doc.title)}</h4>
      <p class="result-snippet">${escapeHtml(doc.snippet || doc.content)}</p>
    `;
    return card;
  }

  function renderEvaluationTable(evalData) {
    evalTableBody.innerHTML = "";

    evalData.results.forEach((row, idx) => {
      const tr = document.createElement("tr");
      const sign = row.improvement_percent >= 0 ? "+" : "";
      tr.innerHTML = `
        <td>${idx + 1}</td>
        <td><strong>${escapeHtml(row.test_query)}</strong></td>
        <td><span class="badge ${row.method === "AI Rewriting" ? "badge-ai" : "badge-fallback"}">${escapeHtml(row.method)}</span></td>
        <td>${escapeHtml(row.top_rewritten_title)}</td>
        <td style="font-family: var(--font-mono);">${Number(row.original_score).toFixed(3)}</td>
        <td style="font-family: var(--font-mono); color: #047857; font-weight: 700;">${Number(row.rewritten_score).toFixed(3)}</td>
        <td><span class="stat-badge-green">${sign}${Number(row.improvement_percent).toFixed(1)}%</span></td>
      `;
      evalTableBody.appendChild(tr);
    });

    const summary = evalData.summary;
    evalMeanOrig.textContent = Number(summary.mean_original_score).toFixed(3);
    evalMeanRewr.textContent = Number(summary.mean_rewritten_score).toFixed(3);
    const overallSign = summary.overall_improvement_percent >= 0 ? "+" : "";
    evalOverallImp.textContent = `${overallSign}${Number(summary.overall_improvement_percent).toFixed(1)}%`;

    evalTableWrapper.classList.remove("hidden");
    evalTableWrapper.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Run initial query on page load
  executeAdvisoryAndRetrieval("mango fruit black spot");
});
