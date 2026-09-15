# 🌾 KrishiQuery AI — Farm Advisory Query Rewriter

> **AGR-25 Hackathon MVP**: Transforming short, informal, and ambiguous farmer questions into high-precision search queries for agricultural RAG & advisory retrieval systems.

---

## 1. Problem Statement

Farmers consulting digital advisory systems or helplines rarely phrase queries like agricultural scientists. Instead of typing:
> *"Tomato leaf curl virus vector management and symptoms"*

They type short, colloquial, and ambiguous queries like:
> *"tomato leaf curling what do"* or *"chilli leaves getting small"* or *"plant has white insects"*

When piped directly into search engines or vector/RAG systems:
- Key domain entities (crop species, pathological symptoms, insect vectors, physiological disorders) are unexpressed.
- Important retrieval keywords are absent, resulting in low similarity scores and irrelevant or noisy documents.
- Farmers receive incorrect, incomplete, or hazardous advisory recommendations.

---

## 2. Proposed Solution & New Advisory Flow

**KrishiQuery AI** acts as an intelligent **pre-retrieval query rewriting and advisory layer**:

```text
Farmer Question ("mango fruit black spot")
       ↓
🧠 AI Query Understanding (Crop: Mango | Plant Part: Fruit | Problem: Black spot | Intent: Diagnosis)
       ↓
🔄 Optimized Query ("Mango fruit black spots: possible causes, symptoms, prevention and management")
       ↓
🔎 Live Web Search & Agricultural Extension Sources (Wikipedia Plant Science, TNAU Agritech, ICAR)
       ↓
💡 Concise Farmer-Friendly Guidance (Diagnostic overview, inspection steps, cultural/IPM practices, safety warning)
```

---

## 3. Architecture

```text
krishiquery-ai/
├── app.py                 # Flask server & REST API (/api/advisory, /api/rewrite-and-search, /api/evaluate)
├── query_rewriter.py      # Dual-mode rewriter: open-domain crop, plant part, symptom & intent extraction
├── web_search.py          # Live web search engine & safe agricultural guidance synthesizer
├── retriever.py           # Scikit-learn TF-IDF + Cosine Similarity local benchmark retrieval engine
├── evaluation.py          # Dynamic benchmark runner across 8 standardized test questions (+95.4% improvement)
├── test_advisory.py       # Automated test suite for unseen queries (mango, banana, onion, etc.)
├── test_e2e.py            # End-to-end integration and benchmark verification test suite
├── requirements.txt       # Dependencies (Flask, scikit-learn, openai, python-dotenv)
├── .env.example           # Environment template (API keys, ports)
├── README.md              # Full documentation & demo guide
│
├── data/
│   └── agriculture.json   # 30 expert-checked, safety-compliant agricultural documents
│
├── templates/
│   └── index.html         # Responsive semantic HTML5 advisory dashboard
│
└── static/
    ├── style.css          # Agricultural green design system, cards, animations
    └── script.js          # Interactive search, advisory flow & live benchmark evaluation
```

---

## 4. Technology Stack

- **Backend**: Python 3.11, Flask 3.1
- **Retrieval Engine**: `scikit-learn` (TF-IDF Vectorizer with 1-2 ngrams, sublinear term frequency, cosine similarity)
- **AI Rewriting**:
  - Primary: OpenAI API (`gpt-4o-mini`) if `OPENAI_API_KEY` is present.
  - Resilient Fallback: Rule-based agricultural entity extractor & terminology expansion engine (100% offline & zero external dependency).
- **Frontend**: Semantic HTML5, Vanilla CSS3 (Custom Agricultural Design System), Vanilla JavaScript.
- **Knowledge Base**: Curated local JSON dataset (30 documents covering 6 key crops).

---

## 5. How Query Rewriting Works

### Prompt & System Instruction
When an API key is configured, the system uses this targeted prompt:
```text
"You are an agricultural search-query rewriter. Convert an informal farmer question into one precise search query for retrieving agricultural advisory documents. Preserve the original meaning. Identify crop, problem, symptom, pest, disease, farming activity, location and season only when explicitly provided. Never invent missing facts. Return a concise optimized agricultural search query."
```

### Dual-Mode Execution & Fallback
1. **AI Mode**: Sends structured JSON prompt to OpenAI. If valid response returns, tagged as `AI Rewriting`.
2. **Fallback Mode**: If no API key is provided or the network call times out, the built-in rule-based agricultural engine automatically detects the crop, problem patterns (e.g. *leaf curling, yellowing, small leaves, white insects, fertilizer schedule*), and intent. Tagged as `Fallback Rewriting`.

---

## 6. Retrieval Method

- Document representations combine **Crop**, **Title** (weighted), and **Content**.
- Query is vectorized using the trained TF-IDF model.
- Cosine similarity is computed against all 30 documents:
  $$\text{Cosine Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$
- Returns Top 3 documents with similarity scores between 0.0 and 1.0.

---

## 7. Before vs After Evaluation

Top-3 similarity comparison formula:
$$\text{Improvement \%} = \frac{\text{Rewritten Avg} - \text{Original Avg}}{\text{Original Avg}} \times 100$$

### Benchmark Results (8 Standard Farmer Questions)
| # | Test Query | Top Document Match | Original Avg | Rewritten Avg | Improvement |
|---|------------|--------------------|--------------|---------------|-------------|
| 1 | `tomato leaf curling what do` | Tomato Leaf Curl Virus (ToLCV) | 0.166 | 0.303 | **+82.5%** |
| 2 | `rice leaves yellow` | Rice Leaves Yellowing: Zinc Deficiency (Khaira) | 0.136 | 0.268 | **+97.1%** |
| 3 | `cotton pest on leaves` | Cotton Sucking Pests: Aphids, Jassids, Thrips | 0.152 | 0.258 | **+69.7%** |
| 4 | `chilli leaves getting small` | Chilli Leaf Curl Virus (Murda Complex) | 0.125 | 0.306 | **+144.8%** |
| 5 | `maize leaves yellow` | Maize Zinc Deficiency (White Bud Disease) | 0.140 | 0.272 | **+94.3%** |
| 6 | `plant has white insects` | Cotton Whitefly Pest Management & Sooty Mold | 0.091 | 0.200 | **+119.8%** |
| 7 | `what fertilizer for rice` | Rice Fertilizer Application & Nitrogen Schedule | 0.138 | 0.216 | **+56.5%** |
| 8 | `groundnut leaves turning brown and drying` | Groundnut Tikka Leaf Spot Disease Control | 0.102 | 0.228 | **+123.5%** |
| **MACRO** | **Overall Average (Mean Scores)** | — | **0.131** | **0.256** | **+95.4%** |

> *Disclaimer: Similarity improvement is a lightweight retrieval indicator, not a measure of factual correctness.*

---

## 8. Installation

### Prerequisites
- Python 3.9+ (or `uv`)

### Setup Commands
```bash
# 1. Navigate to project directory
cd krishiquery-ai

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. (Optional) Configure OpenAI API Key
# Copy .env.example to .env and add your key:
# OPENAI_API_KEY=sk-...
```

---

## 9. How to Run

```bash
# Run Flask web application
python app.py
```

Access the application in your browser:
👉 **`http://127.0.0.1:5000`**

To run standalone benchmark evaluation in terminal:
```bash
python evaluation.py
```

---

## 10. Example User Flow

1. Enter query: `tomato leaf curling what do`
2. Click **Rewrite & Search** (or click a quick example chip).
3. Review **AI Query Analysis**:
   - Crop: **Tomato**
   - Problem: **Leaf curling & puckering**
   - Intent: **Diagnosis / management**
   - Location / Season: **Not specified**
4. Compare **Original vs Rewritten** Top 3 retrieved documents:
   - Original average score: `0.166`
   - Rewritten average score: `0.303`
   - Metric: **Retrieval similarity improved by +82.5%**
5. Click **Evaluate Test Set** to inspect benchmark performance across all 8 standard queries.

---

## 11. Limitations

- **Lexical/TF-IDF Retrieval**: Evaluated on TF-IDF word frequency and n-gram overlap rather than dense vector embeddings.
- **Synthesized Knowledge Base**: Contains 30 representative documents; real-world agricultural deployment requires 100,000+ university extension bulletins.
- **Language Support**: Currently optimized for English agricultural terms; regional vernacular Indian languages (Hindi, Telugu, Tamil, Marathi) require an additional translation stage.

---

## 12. Future Improvements

1. **Multilingual Speech Input**: Direct integration of regional voice inputs (Bhashini / Whisper) converting speech directly to rewritten queries.
2. **Dense Hybrid Retrieval**: Combining BM25/TF-IDF with dense agricultural embeddings (e.g. BioLinkBERT or agricultural sentence transformers).
3. **Geo-location & Weather Grounding**: Automatically injecting localized weather data (e.g., rainfall, humidity) when the farmer provides GPS coordinates.
#   A G R - 2 5  
 