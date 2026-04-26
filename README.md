# ⚡ Catalyst — Skill Assessment & Learning Plan Agent

> Upload your resume and a job description. Get an AI-powered skill gap analysis, match score, and a personalised free learning roadmap — in seconds.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Sample Output](#sample-output)
- [Notes & Limitations](#notes--limitations)

---

## Overview

**Catalyst** is a fully modular, tool-based AI agent that analyses the gap between a candidate's existing skills (from their resume) and the requirements of a target role (from a job description). It produces:

- An **overall match score** (0–100)
- A **skill-by-skill breakdown** with candidate level assessment
- A **prioritised learning roadmap** with curated free resources
- An **estimated upskilling timeline**
- A **chat interface** for follow-up questions about your results

Everything runs on **free and open-source tools** — no paid API keys required.

---

## Features

| Feature | Description |
|---|---|
| 📄 Resume & JD Input | Paste text directly or upload a PDF / DOCX file |
| 🧠 Dual Skill Extraction | Taxonomy keyword matching + HuggingFace LLM extraction |
| 📐 Hybrid Scoring | 4-signal scoring: semantic similarity, keyword match, section boost, frequency |
| 🗺️ Learning Roadmap | Prioritised gaps with free resources (courses, docs, videos) |
| ⏱️ Time Estimate | Upskilling timeline at 10 hrs/week |
| 💬 Chat Interface | Ask follow-up questions about your assessment |
| 📦 JSON Export | Download your full report as structured JSON |
| 🆓 100% Free | Uses sentence-transformers locally + HuggingFace free inference tier |

---

## Architecture

Catalyst follows a linear pipeline of 7 independent tools orchestrated by the `CatalystAgent`:

```
InputParser → SkillExtractor → EmbeddingEngine → ScoringEngine
                                                        ↓
              ExplanationGenerator ← RoadmapBuilder ← (scores)
```

| Tool | Class | Responsibility |
|---|---|---|
| 1 | `InputParser` | Cleans and normalises raw resume + JD text |
| 2 | `SkillExtractor` | Extracts skills via taxonomy keywords + HuggingFace LLM |
| 3 | `EmbeddingEngine` | Generates semantic embeddings using `all-MiniLM-L6-v2` |
| 4 | `ScoringEngine` | Hybrid 4-signal scoring of each JD skill against the resume |
| 5 | `ResourceFinder` | Maps skill gaps to curated free learning resources |
| 6 | `RoadmapBuilder` | Builds a prioritised learning plan with time estimates |
| 7 | `ExplanationGenerator` | Produces a human-readable summary report |

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io/) |
| Local Embeddings | [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) |
| LLM Skill Extraction | [HuggingFace Inference API](https://huggingface.co/inference-api) (Mistral-7B-Instruct, free tier) |
| Similarity | [scikit-learn](https://scikit-learn.org/) cosine similarity |
| PDF Parsing | [pypdf](https://pypdf.readthedocs.io/) |
| DOCX Parsing | [python-docx](https://python-docx.readthedocs.io/) |
| Numerics | [NumPy](https://numpy.org/) |

---

## Installation

### Prerequisites

- Python 3.10 or higher
- `pip`

### Steps

```bash
# 1. Clone or download the project
git clone <your-repo-url>
cd catalyst

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

> **Note:** On first run, the `all-MiniLM-L6-v2` embedding model (~80 MB) will be downloaded automatically from HuggingFace and cached locally.

---

## Configuration

Catalyst works out of the box without any API key. However, adding a free HuggingFace token removes rate limits on the LLM skill extraction step.

Create a `.env` file in the project root:

```env
HF_API_TOKEN=hf_your_token_here
```

Get a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

> Without a token, Catalyst gracefully falls back to keyword-only skill extraction — results are still accurate.

---

## Running the App

```bash
streamlit run streamlit_app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

To run a quick CLI smoke-test instead:

```bash
python catalyst_agent.py
```

---

## How It Works

### Skill Extraction (Tool 2)
Skills are extracted using two strategies in parallel:

1. **Taxonomy matching** — a curated dictionary of 30+ skill categories with aliases (e.g. `"ml"`, `"sklearn"`, `"scikit-learn"` all map to `"machine learning"`) catches common skills reliably.
2. **LLM extraction** — a Mistral-7B prompt extracts any skills not in the taxonomy. Results from both are merged and deduplicated, with taxonomy results taking priority.

### Hybrid Scoring (Tool 4)
Each JD skill is scored (0–100) using 4 independent signals:

| Signal | Weight | Description |
|---|---|---|
| Semantic similarity | High | Cosine similarity of skill embedding vs. resume sentences |
| Keyword presence | Medium | Exact/alias keyword match in resume |
| Section boost | Medium | Bonus if skill found in key sections (Skills, Experience) |
| Frequency | Low | How often the skill appears in the resume |

The overall match score is a weighted average across all JD skills, with core skills weighted higher than nice-to-haves.

### Candidate Levels
Each skill is classified into one of three levels:

- ✅ **Strong** — score ≥ 65
- ⚠️ **Partial** — score 35–64
- ❌ **Missing** — score < 35

### Learning Roadmap (Tool 6)
Gap skills are prioritised by:
- Whether the skill is core (required) or nice-to-have
- The severity of the gap (lower score = higher priority)

Each skill in the roadmap includes:
- Estimated learning hours (e.g. `20–60 hrs`)
- A milestone description
- 2–3 curated free resources (courses, docs, YouTube videos)

Time estimates assume **10 hours/week** of study.

---

## Project Structure

```
catalyst/
├── catalyst_agent.py     # Core agent: all 7 tools + data models
├── streamlit_app.py      # Streamlit UI (Input, Results, Chat tabs)
├── requirements.txt      # Python dependencies
├── .env                  # (Optional) HF_API_TOKEN — not committed to git
└── README.md
```

---

## Sample Output

```
📊 Overall Match Score: 61/100

✅ Strengths (4):
   • python
   • machine learning
   • data analysis
   • communication

🔧 Skill Gaps (4):
   • deep learning
   • sql
   • docker
   • kubernetes

🟡 Moderate fit — focused learning can bridge the gap.
⏱  Estimated time to bridge gaps: ~19 weeks (at 10 hrs/week)
```

---

## Notes & Limitations

- **HuggingFace free tier** can be slow or temporarily unavailable during high traffic periods. Catalyst automatically falls back to keyword-only extraction in these cases.
- **Skill taxonomy coverage** is broad but not exhaustive. Highly niche or emerging skills not in the taxonomy will only be detected if the HuggingFace LLM extraction succeeds.
- **Resume parsing quality** depends on the text content of the uploaded file. Scanned PDFs (image-only) cannot be parsed.
- The **chat tab** uses rule-based responses — it does not make additional LLM calls, so responses are instant but limited to assessment-related topics.
- FAISS vector search is listed in `requirements.txt` as a comment. Uncomment `faiss-cpu` to enable it if you need faster similarity search at scale.

---

*Built for the Catalyst Hackathon. All tools used are free and open-source.*
