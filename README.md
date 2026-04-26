# ⚡ Catalyst — Skill Assessment & Learning Plan Agent

> An AI-powered, production-ready agent that analyses your resume against a job description, identifies skill gaps, and generates a personalised free-resource learning roadmap.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-ff4b4b)](https://streamlit.io/)
[![Free Tier Only](https://img.shields.io/badge/APIs-Free%20Tier%20Only-34d399)](https://huggingface.co/)
[![Open Source](https://img.shields.io/badge/models-Open%20Source-f59e0b)](https://huggingface.co/sentence-transformers)

---

## 🎯 What It Does

| Input | Output |
|-------|--------|
| Resume (plain text) | Overall match score (0–100) |
| Job Description (plain text) | Per-skill scores with explanations |
| | Strengths & gap analysis |
| | Prioritised learning roadmap |
| | Free curated resources (YouTube, docs, courses) |
| | Estimated upskilling timeline |
| | Downloadable JSON report |

---

## 🏗️ Architecture

```
catalyst-project/
├── catalyst_agent.py            ← Core agent (7 modular tools)
├── streamlit_app.py    ← UI layer
├── requirements.txt
└── README.md
```

### Agent Pipeline

```
Resume + JD
    │
    ▼
┌─────────────┐     ┌──────────────────┐
│ InputParser │────▶│  SkillExtractor  │  Taxonomy + HF LLM
└─────────────┘     └──────────────────┘
                           │
                    ┌──────▼──────────┐
                    │ EmbeddingEngine │  sentence-transformers (local)
                    └──────┬──────────┘
                           │
                    ┌──────▼──────────┐
                    │  ScoringEngine  │  Cosine similarity + keyword boost
                    └──────┬──────────┘
                           │
                    ┌──────▼──────────┐
                    │ RoadmapBuilder  │  Priority-sorted learning items
                    └──────┬──────────┘
                           │
                    ┌──────▼──────────┐
                    │ExplanationGen.  │  Human-readable summary
                    └──────┬──────────┘
                           │
                    AssessmentResult (JSON + UI)
```

### Scoring Formula

```
base_score   = cosine_similarity(skill_embedding, resume_embedding) × 100
keyword_boost = +15 if exact keyword in resume
final_score  = min(100, base_score + keyword_boost)

overall_match = Σ(score × weight) / Σ(weight)
  where weight = 2.0 for core skills, 1.0 for nice-to-haves
```

### Candidate Level Labels
| Score Range | Label |
|-------------|-------|
| ≥ 65 | Strong ✅ |
| 35–64 | Partial ⚠️ |
| < 35 | Missing ❌ |

---

## 🚀 Setup & Run

### 1. Clone / navigate to project

```bash
cd catalyst-project
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> First run downloads the `all-MiniLM-L6-v2` embedding model (~80 MB). No signup required.

### 4. (Optional) HuggingFace API token

The agent works fully without a token (keyword extraction only). To enable LLM-powered skill extraction, add your **free** HF token:

```bash
# Create .env file
echo "HF_API_TOKEN=hf_your_token_here" > .env
```

Get a free token at https://huggingface.co/settings/tokens

### 5. Run the app

```bash
streamlit run streamlit_app.py
```

Open http://localhost:8501 in your browser.

### 6. Quick CLI test

```bash
python catalyst_agent.py
```

---

## 💻 Usage

1. **Input Tab** — Paste your resume and the job description (sample data pre-filled)
2. Click **⚡ Analyse Skills & Generate Roadmap**
3. Switch to **Results Tab** — view:
   - Overall match score
   - Skill-by-skill breakdown with visual bars
   - Strengths & gaps as colour-coded pills
   - Full learning roadmap with free resources
4. **Chat Tab** — ask follow-up questions (no API key needed)
5. **Sidebar** — download full JSON report

---

## 🛠️ Tech Stack (100% Free)

| Component | Technology | Cost |
|-----------|-----------|------|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Free / local |
| LLM skill extraction | HuggingFace Inference API (Mistral-7B) | Free tier |
| Similarity | `sklearn.metrics.pairwise.cosine_similarity` | Free |
| UI | Streamlit | Free / open-source |
| Resources | Curated free links (YouTube, Coursera audit, freeCodeCamp, etc.) | Free |

---

## 🔥 Key Features

- **Dual skill extraction**: taxonomy keyword matching + LLM (best of both)
- **Embedding cache**: avoids redundant computation
- **Graceful fallback**: works offline / without HF token (keyword mode)
- **Session memory**: chat retains context across turns
- **Download as JSON**: full structured output
- **Responsive UI**: works on desktop and mobile browsers
- **No paid API required**: 100% free to run

---

## 📊 Sample Output (JSON)

```json
{
  "overall_match_score": 62.4,
  "strengths": ["python", "javascript", "react", "git"],
  "gaps": ["docker", "aws", "node.js", "kubernetes"],
  "estimated_weeks": 14,
  "skill_scores": [
    {
      "skill": "python",
      "required_level": "core",
      "candidate_level": "strong",
      "score": 88.2,
      "explanation": "Candidate demonstrates solid python knowledge (score 88/100)."
    }
  ],
  "learning_roadmap": [
    {
      "skill": "docker",
      "priority": "high",
      "estimated_hours": [20, 60],
      "milestone": "Complete a beginner project using docker",
      "resources": [
        {
          "title": "Docker Official Get Started",
          "url": "https://docs.docker.com/get-started/",
          "resource_type": "docs"
        }
      ]
    }
  ]
}
```

---

## 🧩 Extending the Agent

- **Add skills to taxonomy**: edit `SKILL_TAXONOMY` in `agent.py`
- **Add resources**: edit `RESOURCE_LIBRARY` in `agent.py`
- **Swap LLM**: change `HF_API_URL` to any free HuggingFace model
- **Add FAISS**: uncomment `faiss-cpu` in `requirements.txt` and extend `EmbeddingEngine`

---

## 📄 License

MIT — free to use, modify, and distribute.

---

Built with ⚡ for the Catalyst Hackathon
