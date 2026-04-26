"""
Catalyst Agent — Skill Assessment & Learning Plan Agent
========================================================
A fully modular, tool-based AI agent that:
  1. Parses resume + job description
  2. Extracts required & existing skills
  3. Identifies skill gaps
  4. Scores each skill (0–100)
  5. Generates a learning roadmap with free resources
  6. Produces structured JSON output + human-readable explanation

Uses ONLY free-tier / open-source models:
  - sentence-transformers (local, free)
  - HuggingFace Inference API (free tier) for text generation
  - YouTube Data-free search via web scraping / yt-search-python
  - FAISS for vector similarity (optional, falls back to cosine)

Author: Catalyst Hackathon Team
"""

import os
import re
import json
import time
import math
import hashlib
import logging
from typing import Any
from dataclasses import dataclass, field, asdict

import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("catalyst.agent")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")          # optional – speeds up HF
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"                 # ~80 MB, fully free/local
YT_SEARCH_ENDPOINT = "https://www.youtube.com/results"

# Skill taxonomy — broadens keyword recall for common domains
SKILL_TAXONOMY = {
    "python": ["python", "python3", "py", "python2", "flask", "fastapi", "django"],
    "machine learning": ["machine learning", "ml", "sklearn", "scikit-learn", "scikit learn"],
    "deep learning": ["deep learning", "dl", "neural network", "pytorch", "tensorflow", "keras", "torch"],
    "nlp": ["nlp", "natural language processing", "text mining", "hugging face", "transformers", "spacy"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "database", "rdbms", "pl/sql", "t-sql"],
    "docker": ["docker", "containerization", "container", "dockerfile"],
    "kubernetes": ["kubernetes", "k8s", "container orchestration", "helm", "kubectl"],
    "aws": ["aws", "amazon web services", "cloud", "ec2", "s3", "lambda", "azure", "gcp", "google cloud", "cloud computing", "oracle cloud", "oci"],
    "react": ["react", "reactjs", "react.js", "react native", "redux"],
    "node.js": ["node", "nodejs", "node.js", "express", "expressjs"],
    "javascript": ["javascript", "js", "es6", "typescript", "ts", "jquery"],
    "java": ["java", "spring", "spring boot", "springboot", "j2ee", "jvm"],
    "git": ["git", "github", "gitlab", "version control", "bitbucket", "source control"],
    "agile": ["agile", "scrum", "kanban", "sprint", "jira", "scrum fundamentals"],
    "data analysis": ["data analysis", "data analytics", "pandas", "numpy", "excel", "data science"],
    "visualization": ["visualization", "tableau", "power bi", "matplotlib", "seaborn", "plotly", "charts"],
    "communication": ["communication", "presentation", "public speaking", "stakeholder", "soft skills", "time management"],
    "leadership": ["leadership", "management", "team lead", "mentoring", "mentor"],
    "statistics": ["statistics", "statistical analysis", "hypothesis testing", "regression"],
    "api": ["api", "rest api", "restful", "graphql", "fastapi", "flask", "django", "rest"],
    "devops": ["devops", "ci/cd", "jenkins", "github actions", "terraform", "ci cd", "pipeline"],
    "linux": ["linux", "unix", "bash", "shell scripting", "shell"],
    "c++": ["c++", "cpp", "c plus plus"],
    "r": [" r ", "r programming", "rstudio"],
    "html/css": ["html", "css", "bootstrap", "tailwind", "web development", "frontend", "front-end"],
    "android": ["android", "android studio", "mobile development", "kotlin"],
    "mongodb": ["mongodb", "mongo", "nosql", "no-sql"],
    "c": [" c ", "c language", "data structures in c", "c programming"],
    # ── AI / LLM skills (Cognizant JD specific) ──────────────────────
    "llm": ["llm", "large language model", "gpt", "claude", "gemini", "mistral", "llama", "language model", "generative ai", "gen ai", "genai", "ai model"],
    "rag": ["rag", "retrieval augmented generation", "retrieval-augmented", "vector search", "vector db", "vector database", "embedding", "embeddings", "langchain", "langgraph", "llamaindex"],
    "prompt engineering": ["prompt engineering", "prompt", "prompt template", "prompt design", "structured output", "tool calling", "function calling", "introduction to prompt engineering"],
    "agentic ai": ["agentic", "agent", "ai agent", "autogen", "crewai", "multi-agent", "workflow automation", "langchain", "langgraph"],
    "ai evaluation": ["ai evaluation", "ai quality", "hallucination", "guardrails", "ragas", "deepeval", "monitoring", "ai ops", "ai testing"],
    "cloud native": ["cloud native", "microservices", "serverless", "event-driven", "ci/cd", "containers"],
    "salesforce": ["salesforce", "crm", "salesforce administrator", "trailhead", "salesforce admin"],
    "hashgraph": ["hashgraph", "hedera", "blockchain", "distributed ledger"],
    "full stack": ["full stack", "fullstack", "full-stack", "end-to-end", "mern", "mean"],
}

# Free learning resources per skill category
RESOURCE_LIBRARY = {
    "python": [
        {"title": "Python for Everybody (Coursera Free Audit)", "url": "https://www.coursera.org/specializations/python", "type": "course"},
        {"title": "Official Python Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "docs"},
    ],
    "machine learning": [
        {"title": "ML Crash Course — Google", "url": "https://developers.google.com/machine-learning/crash-course", "type": "course"},
        {"title": "fast.ai Practical Deep Learning", "url": "https://course.fast.ai/", "type": "course"},
    ],
    "deep learning": [
        {"title": "DeepLearning.AI Specialization (Audit)", "url": "https://www.deeplearning.ai/courses/", "type": "course"},
        {"title": "PyTorch Official Tutorials", "url": "https://pytorch.org/tutorials/", "type": "docs"},
    ],
    "sql": [
        {"title": "SQLZoo Interactive SQL", "url": "https://sqlzoo.net/", "type": "interactive"},
        {"title": "Mode SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "course"},
    ],
    "docker": [
        {"title": "Docker Official Get Started", "url": "https://docs.docker.com/get-started/", "type": "docs"},
        {"title": "Docker Tutorial for Beginners — TechWorld (YouTube)", "url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "type": "video"},
    ],
    "aws": [
        {"title": "AWS Free Tier + Training", "url": "https://aws.amazon.com/training/", "type": "course"},
        {"title": "Cloud Practitioner Essentials", "url": "https://explore.skillbuilder.aws/learn/course/134", "type": "course"},
    ],
    "react": [
        {"title": "React Official Docs", "url": "https://react.dev/learn", "type": "docs"},
        {"title": "Full React Course — freeCodeCamp (YouTube)", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8", "type": "video"},
    ],
    "javascript": [
        {"title": "javascript.info — Modern JS Tutorial", "url": "https://javascript.info/", "type": "docs"},
        {"title": "freeCodeCamp JS Algorithms", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "type": "interactive"},
    ],
    "git": [
        {"title": "Pro Git Book (Free)", "url": "https://git-scm.com/book/en/v2", "type": "docs"},
        {"title": "Git & GitHub Crash Course (YouTube)", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk", "type": "video"},
    ],
    "statistics": [
        {"title": "Khan Academy Statistics", "url": "https://www.khanacademy.org/math/statistics-probability", "type": "course"},
        {"title": "StatQuest with Josh Starmer (YouTube)", "url": "https://www.youtube.com/@statquest", "type": "video"},
    ],
    "nlp": [
        {"title": "HuggingFace NLP Course (Free)", "url": "https://huggingface.co/learn/nlp-course", "type": "course"},
        {"title": "Stanford CS224N (YouTube)", "url": "https://www.youtube.com/playlist?list=PLoROMvodv4rOSH4v6133s9LFPRHjEmbmJ", "type": "video"},
    ],
    "data analysis": [
        {"title": "Kaggle — Data Analysis Course", "url": "https://www.kaggle.com/learn/pandas", "type": "interactive"},
        {"title": "Pandas Official Docs", "url": "https://pandas.pydata.org/docs/", "type": "docs"},
    ],
    "devops": [
        {"title": "DevOps Roadmap", "url": "https://roadmap.sh/devops", "type": "docs"},
        {"title": "GitHub Actions Documentation", "url": "https://docs.github.com/en/actions", "type": "docs"},
    ],
    "linux": [
        {"title": "The Linux Command Line (Free Book)", "url": "https://linuxcommand.org/tlcl.php", "type": "docs"},
        {"title": "Linux Basics — MIT OCW (YouTube)", "url": "https://www.youtube.com/watch?v=ysENRCv07K0", "type": "video"},
    ],
    "kubernetes": [
        {"title": "Kubernetes Official Docs", "url": "https://kubernetes.io/docs/tutorials/", "type": "docs"},
        {"title": "TechWorld Kubernetes Course (YouTube)", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "type": "video"},
    ],
    "agile": [
        {"title": "Atlassian Agile Guide", "url": "https://www.atlassian.com/agile", "type": "docs"},
        {"title": "Scrum Guide (Official Free)", "url": "https://scrumguides.org/", "type": "docs"},
    ],
    # ── AI / LLM skills ──────────────────────────────────────────────
    "llm": [
        {"title": "HuggingFace LLM Course (Free)", "url": "https://huggingface.co/learn/llm-course", "type": "course"},
        {"title": "Andrej Karpathy — Let's Build GPT (YouTube)", "url": "https://www.youtube.com/watch?v=kCc8FmEb1nY", "type": "video"},
        {"title": "LLM Bootcamp — Full Stack Deep Learning", "url": "https://fullstackdeeplearning.com/llm-bootcamp/", "type": "course"},
    ],
    "rag": [
        {"title": "LangChain RAG Tutorial (Official Docs)", "url": "https://python.langchain.com/docs/tutorials/rag/", "type": "docs"},
        {"title": "RAG from Scratch — DeepLearning.AI (Free)", "url": "https://learn.deeplearning.ai/courses/building-systems-with-chatgpt", "type": "course"},
        {"title": "LlamaIndex Starter Tutorial", "url": "https://docs.llamaindex.ai/en/stable/getting_started/starter_example/", "type": "docs"},
    ],
    "prompt engineering": [
        {"title": "Prompt Engineering Guide (Free)", "url": "https://www.promptingguide.ai/", "type": "docs"},
        {"title": "DeepLearning.AI — ChatGPT Prompt Engineering (Free)", "url": "https://learn.deeplearning.ai/courses/chatgpt-prompt-eng", "type": "course"},
        {"title": "Anthropic Prompt Engineering Docs", "url": "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview", "type": "docs"},
    ],
    "agentic ai": [
        {"title": "LangGraph Tutorial (Official)", "url": "https://langchain-ai.github.io/langgraph/tutorials/introduction/", "type": "docs"},
        {"title": "DeepLearning.AI — AI Agents (Free)", "url": "https://learn.deeplearning.ai/courses/ai-agents-in-langgraph", "type": "course"},
        {"title": "AutoGen Microsoft Tutorial", "url": "https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/introduction.html", "type": "docs"},
    ],
    "ai evaluation": [
        {"title": "RAGAS Documentation", "url": "https://docs.ragas.io/en/stable/", "type": "docs"},
        {"title": "DeepEval LLM Evaluation", "url": "https://docs.confident-ai.com/", "type": "docs"},
    ],
    "full stack": [
        {"title": "Full Stack Open (University of Helsinki — Free)", "url": "https://fullstackopen.com/en/", "type": "course"},
        {"title": "The Odin Project (Free)", "url": "https://www.theodinproject.com/", "type": "interactive"},
    ],
    "html/css": [
        {"title": "freeCodeCamp Responsive Web Design", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "type": "interactive"},
        {"title": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/docs/Learn", "type": "docs"},
    ],
    "node.js": [
        {"title": "Node.js Official Docs", "url": "https://nodejs.org/en/learn/getting-started/introduction-to-nodejs", "type": "docs"},
        {"title": "Node.js Crash Course (YouTube)", "url": "https://www.youtube.com/watch?v=fBNz5xF-Kx4", "type": "video"},
    ],
    "java": [
        {"title": "NPTEL Java Programming (Free)", "url": "https://nptel.ac.in/courses/106/105/106105191/", "type": "course"},
        {"title": "Codecademy Learn Java (Free tier)", "url": "https://www.codecademy.com/learn/learn-java", "type": "interactive"},
    ],
    "cloud native": [
        {"title": "CNCF Cloud Native Landscape", "url": "https://landscape.cncf.io/", "type": "docs"},
        {"title": "Google Cloud Skills Boost (Free paths)", "url": "https://www.cloudskillsboost.google/", "type": "course"},
    ],
}

DEFAULT_RESOURCE = [
    {"title": "Search on YouTube", "url": "https://www.youtube.com/results?search_query=", "type": "video"},
    {"title": "Search on freeCodeCamp", "url": "https://www.freecodecamp.org/news/search/?query=", "type": "course"},
]

# Effort estimates (hours) per skill proficiency tier
HOURS_ESTIMATE = {
    "beginner → intermediate": (20, 60),
    "intermediate → advanced": (40, 120),
    "no exposure → beginner": (10, 30),
}


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------
@dataclass
class SkillScore:
    skill: str
    required_level: str          # "core" | "nice-to-have"
    candidate_level: str         # "strong" | "partial" | "missing"
    score: float                 # 0–100
    explanation: str


@dataclass
class LearningResource:
    title: str
    url: str
    resource_type: str           # "video" | "course" | "docs" | "interactive"


@dataclass
class LearningItem:
    skill: str
    priority: str                # "high" | "medium" | "low"
    estimated_hours: tuple
    resources: list[LearningResource]
    milestone: str


@dataclass
class AssessmentResult:
    overall_match_score: float
    skill_scores: list[SkillScore]
    strengths: list[str]
    gaps: list[str]
    learning_roadmap: list[LearningItem]
    estimated_weeks: int
    explanation: str
    raw_jd_skills: list[str]
    raw_resume_skills: list[str]
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Tool 1 — Input Parser
# ---------------------------------------------------------------------------
class InputParser:
    """Cleans and normalises raw resume + JD text."""

    @staticmethod
    def clean(text: str) -> str:
        """Strip URLs, extra whitespace, and control characters."""
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"[^\x20-\x7E\n]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def parse(self, resume_text: str, jd_text: str) -> dict[str, str]:
        logger.info("InputParser: cleaning inputs")
        return {
            "resume": self.clean(resume_text),
            "jd": self.clean(jd_text),
        }


# ---------------------------------------------------------------------------
# Tool 2 — Skill Extractor
# ---------------------------------------------------------------------------
class SkillExtractor:
    """
    Dual-strategy skill extraction:
      1. Taxonomy keyword matching (fast, deterministic)
      2. HuggingFace LLM extraction (richer, catches unusual skills)
    Results are merged and deduplicated.
    """

    def __init__(self):
        self.taxonomy = SKILL_TAXONOMY
        self.hf_token = HF_API_TOKEN

    # -- Taxonomy keyword scan ------------------------------------------
    def _keyword_extract(self, text: str) -> list[str]:
        text_lower = text.lower()
        found = []
        for canonical, aliases in self.taxonomy.items():
            for alias in aliases:
                if re.search(r"\b" + re.escape(alias) + r"\b", text_lower):
                    found.append(canonical)
                    break
        return list(dict.fromkeys(found))   # preserve order, dedupe

    # -- HuggingFace LLM extraction -------------------------------------
    def _llm_extract(self, text: str, context: str = "job description") -> list[str]:
        """Call HuggingFace Inference API; gracefully falls back on failure."""
        prompt = (
            f"[INST] Extract a concise list of technical and professional skills "
            f"from the following {context}. Return ONLY a comma-separated list. "
            f"No explanations.\n\n{text[:1500]} [/INST]"
        )
        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"

        try:
            resp = requests.post(
                HF_API_URL,
                headers=headers,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 200, "temperature": 0.1}},
                timeout=30,
            )
            if resp.status_code == 200:
                raw = resp.json()
                if isinstance(raw, list) and raw:
                    generated = raw[0].get("generated_text", "")
                    # Isolate the model's answer after [/INST]
                    answer = generated.split("[/INST]")[-1].strip()
                    skills = [s.strip().lower() for s in answer.split(",") if s.strip()]
                    return [s for s in skills if 2 < len(s) < 50]
            logger.warning("HF API non-200: %s — using keyword-only fallback", resp.status_code)
        except Exception as exc:
            logger.warning("HF API error: %s — using keyword-only fallback", exc)
        return []

    def extract(self, text: str, context: str = "job description") -> list[str]:
        keyword_skills = self._keyword_extract(text)
        llm_skills = self._llm_extract(text, context)
        # Merge: keyword skills first (more reliable), then LLM additions
        merged = keyword_skills[:]
        for s in llm_skills:
            if s not in merged:
                merged.append(s)
        logger.info("SkillExtractor [%s]: found %d skills", context, len(merged))
        return merged


# ---------------------------------------------------------------------------
# Tool 3 — Embedding Engine
# ---------------------------------------------------------------------------
class EmbeddingEngine:
    """
    Wraps sentence-transformers for semantic similarity.
    Caches embeddings per text hash to avoid redundant computation.
    """

    def __init__(self, model_name: str = EMBED_MODEL_NAME):
        logger.info("Loading embedding model: %s", model_name)
        self._model = SentenceTransformer(model_name)
        self._cache: dict[str, np.ndarray] = {}

    def _hash(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def embed(self, text: str) -> np.ndarray:
        key = self._hash(text)
        if key not in self._cache:
            self._cache[key] = self._model.encode(text, normalize_embeddings=True)
        return self._cache[key]

    def similarity(self, a: str, b: str) -> float:
        ea, eb = self.embed(a), self.embed(b)
        return float(cosine_similarity([ea], [eb])[0][0])

    def batch_similarity(self, source: str, targets: list[str]) -> list[float]:
        es = self.embed(source)
        et = self._model.encode(targets, normalize_embeddings=True)
        return cosine_similarity([es], et)[0].tolist()


# ---------------------------------------------------------------------------
# Tool 4 — Matching & Scoring Engine
# ---------------------------------------------------------------------------
class ScoringEngine:
    """
    Accurate hybrid scoring engine — 4 independent signals combined.

    WHY the old approach failed:
      cosine_similarity("python", full_resume_text) is always low (~20-30)
      because the resume embedding averages 500+ words, drowning out any
      single skill. A resume clearly listing Python still scored it as missing.

    NEW APPROACH — 4 signals, each contributing a sub-score (0-100):

    Signal 1 — Exact keyword match (weight 0.40)
      Checks all taxonomy aliases of the skill against resume text.
      Exact match = 100, no match = 0. Most reliable signal.

    Signal 2 — Resume skills set intersection (weight 0.25)
      Whether SkillExtractor already found this skill in the resume.
      If yes = 100. Confirms multi-method detection.

    Signal 3 — Context window similarity (weight 0.25)
      Extract resume sentences that mention any alias of the skill,
      then compare that focused chunk against the skill name using
      cosine similarity. Far more accurate than full-doc comparison.

    Signal 4 — Full-doc semantic similarity (weight 0.10)
      Kept for partial-exposure detection (e.g. adjacent skills),
      but given low weight so it can't dominate.

    Thresholds (tuned empirically):
      strong  ≥ 60   (keyword match alone hits 40, + resume_skills = 65)
      partial  30–59
      missing  < 30
    """

    # Signal weights — must sum to 1.0
    W_KEYWORD  = 0.40
    W_SET      = 0.25
    W_CONTEXT  = 0.25
    W_SEMANTIC = 0.10

    def __init__(self, embedder: EmbeddingEngine):
        self.embedder = embedder

    # ── Signal 1: exact keyword / alias match ──────────────────────────
    def _keyword_score(self, skill: str, resume_lower: str) -> float:
        """Returns 100 if any known alias of the skill appears in resume, else 0."""
        aliases = SKILL_TAXONOMY.get(skill, [skill])
        for alias in aliases:
            # Use word-boundary search; allow common variants (e.g. "python3")
            pattern = r"\b" + re.escape(alias.lower()) + r"\b"
            if re.search(pattern, resume_lower):
                return 100.0
        return 0.0

    # ── Signal 2: resume_skills set intersection ───────────────────────
    def _set_score(self, skill: str, resume_skills: list[str]) -> float:
        """Returns 100 if skill was independently extracted from resume."""
        resume_set = set(s.lower().strip() for s in resume_skills)
        if skill.lower() in resume_set:
            return 100.0
        # Check partial alias match too
        for alias in SKILL_TAXONOMY.get(skill, []):
            if alias.lower() in resume_set or any(alias.lower() in rs for rs in resume_set):
                return 80.0
        return 0.0

    # ── Signal 3: context-window similarity ───────────────────────────
    def _context_score(self, skill: str, resume_sentences: list[str]) -> float:
        """
        Find sentences that mention the skill or its aliases,
        then do cosine similarity on that focused chunk.
        If no sentences match, fall back to 0 (not penalised by full-doc noise).
        """
        aliases = SKILL_TAXONOMY.get(skill, [skill])
        matched = []
        for sent in resume_sentences:
            sent_lower = sent.lower()
            for alias in aliases:
                if alias.lower() in sent_lower:
                    matched.append(sent)
                    break

        if not matched:
            return 0.0

        chunk = " ".join(matched[:5])   # cap at 5 sentences for speed
        sim = self.embedder.similarity(skill, chunk)
        # Cosine similarity for a focused chunk is reliable — scale to 0-100
        # Typical range is 0.35–0.85 for genuine matches
        return min(100.0, sim * 130)    # scale so 0.77 → 100

    # ── Signal 4: full-doc semantic similarity (background) ───────────
    def _semantic_score(self, skill: str, resume_text: str) -> float:
        sim = self.embedder.similarity(skill, resume_text)
        return min(100.0, sim * 130)

    # ── Evidence builder (for explanation text) ───────────────────────
    def _collect_evidence(self, skill: str, resume_sentences: list[str]) -> list[str]:
        """Return up to 2 resume sentences that mention the skill."""
        aliases = SKILL_TAXONOMY.get(skill, [skill])
        evidence = []
        for sent in resume_sentences:
            sent_lower = sent.lower()
            if any(a.lower() in sent_lower for a in aliases):
                evidence.append(sent.strip())
            if len(evidence) >= 2:
                break
        return evidence

    # ── Main scoring method ────────────────────────────────────────────
    def score_skill(
        self,
        skill: str,
        resume_text: str,
        resume_lower: str,
        resume_sentences: list[str],
        resume_skills: list[str],
        is_core: bool,
    ) -> SkillScore:

        s1 = self._keyword_score(skill, resume_lower)
        s2 = self._set_score(skill, resume_skills)
        s3 = self._context_score(skill, resume_sentences)
        s4 = self._semantic_score(skill, resume_text)

        score = round(
            s1 * self.W_KEYWORD
            + s2 * self.W_SET
            + s3 * self.W_CONTEXT
            + s4 * self.W_SEMANTIC,
            1,
        )
        score = max(0.0, min(100.0, score))

        # Collect evidence for explanation
        evidence = self._collect_evidence(skill, resume_sentences)

        if score >= 60:
            level = "strong"
            if evidence:
                expl = f"Confirmed in resume: \"{evidence[0][:120]}\". Score: {score:.0f}/100."
            else:
                expl = f"Strong match — skill detected via keyword and/or semantic analysis. Score: {score:.0f}/100."
        elif score >= 30:
            level = "partial"
            if evidence:
                expl = f"Partial evidence found: \"{evidence[0][:120]}\". Deeper experience may be needed. Score: {score:.0f}/100."
            else:
                expl = f"Adjacent or indirect exposure detected — not explicitly stated in resume. Score: {score:.0f}/100."
        else:
            level = "missing"
            expl = f"No mention or evidence of {skill} found in resume. Score: {score:.0f}/100."

        return SkillScore(
            skill=skill,
            required_level="core" if is_core else "nice-to-have",
            candidate_level=level,
            score=score,
            explanation=expl,
        )

    def score_all(
        self,
        jd_skills: list[str],
        resume_text: str,
        resume_skills: list[str],
    ) -> tuple[list[SkillScore], float]:
        """
        Score every JD skill against the resume.
        Core skills = first 60% of the JD skill list.
        Returns (skill_scores, overall_match_0_100).
        """
        # Pre-process once — avoid recomputing per skill
        resume_lower = resume_text.lower()
        # Split into sentences (simple but effective)
        resume_sentences = [
            s.strip() for s in re.split(r"[.\n;]", resume_text) if len(s.strip()) > 10
        ]

        core_cutoff = max(1, math.ceil(len(jd_skills) * 0.6))
        scores: list[SkillScore] = []

        for i, skill in enumerate(jd_skills):
            is_core = i < core_cutoff
            ss = self.score_skill(
                skill, resume_text, resume_lower, resume_sentences, resume_skills, is_core
            )
            scores.append(ss)

        if not scores:
            return [], 0.0

        # Weighted overall: core skills count 2×, nice-to-have count 1×
        weighted_sum = sum(
            ss.score * (2.0 if ss.required_level == "core" else 1.0) for ss in scores
        )
        weight_total = sum(
            2.0 if ss.required_level == "core" else 1.0 for ss in scores
        )
        overall = round(weighted_sum / weight_total, 1)
        return scores, overall


# ---------------------------------------------------------------------------
# Tool 5 — Resource Finder
# ---------------------------------------------------------------------------
class ResourceFinder:
    """Maps skills to curated free learning resources."""

    def get_resources(self, skill: str) -> list[LearningResource]:
        key = skill.lower().strip()
        # Try exact match, then partial
        resources = RESOURCE_LIBRARY.get(key)
        if not resources:
            for lib_key, lib_res in RESOURCE_LIBRARY.items():
                if lib_key in key or key in lib_key:
                    resources = lib_res
                    break
        if not resources:
            resources = [
                {
                    "title": f"YouTube: learn {skill}",
                    "url": f"https://www.youtube.com/results?search_query=learn+{skill.replace(' ', '+')}",
                    "type": "video",
                },
                {
                    "title": f"freeCodeCamp: {skill}",
                    "url": f"https://www.freecodecamp.org/news/search/?query={skill.replace(' ', '+')}",
                    "type": "course",
                },
            ]
        return [LearningResource(r["title"], r["url"], r["type"]) for r in resources]


# ---------------------------------------------------------------------------
# Tool 6 — Roadmap Builder
# ---------------------------------------------------------------------------
class RoadmapBuilder:
    """
    Generates a prioritised learning roadmap for skill gaps.
    Priority: core missing > core partial > nice-to-have missing > nice-to-have partial
    """

    def __init__(self, resource_finder: ResourceFinder):
        self.resource_finder = resource_finder

    def _priority(self, ss: SkillScore) -> tuple[int, float]:
        level_order = {"missing": 0, "partial": 1, "strong": 2}
        req_order = {"core": 0, "nice-to-have": 1}
        return (req_order[ss.required_level], level_order[ss.candidate_level], -ss.score)

    def _estimate_hours(self, ss: SkillScore) -> tuple[int, int]:
        if ss.candidate_level == "missing":
            lo, hi = HOURS_ESTIMATE["no exposure → beginner"]
        elif ss.candidate_level == "partial":
            lo, hi = HOURS_ESTIMATE["beginner → intermediate"]
        else:
            lo, hi = HOURS_ESTIMATE["intermediate → advanced"]
        return lo, hi

    def _milestone(self, ss: SkillScore) -> str:
        templates = {
            "missing": f"Complete a beginner project using {ss.skill}",
            "partial": f"Build an intermediate-level {ss.skill} project and document it",
            "strong": f"Contribute to open-source or mentor others in {ss.skill}",
        }
        return templates[ss.candidate_level]

    def build(self, skill_scores: list[SkillScore]) -> tuple[list[LearningItem], int]:
        gaps = [ss for ss in skill_scores if ss.candidate_level in ("missing", "partial")]
        gaps.sort(key=self._priority)

        roadmap: list[LearningItem] = []
        total_min_hours = 0
        total_max_hours = 0

        for ss in gaps:
            lo, hi = self._estimate_hours(ss)
            priority = (
                "high" if ss.required_level == "core" and ss.candidate_level == "missing"
                else "medium" if ss.required_level == "core"
                else "low"
            )
            resources = self.resource_finder.get_resources(ss.skill)
            roadmap.append(
                LearningItem(
                    skill=ss.skill,
                    priority=priority,
                    estimated_hours=(lo, hi),
                    resources=resources,
                    milestone=self._milestone(ss),
                )
            )
            total_min_hours += lo
            total_max_hours += hi

        # Assume 10 hours/week study pace → weeks
        estimated_weeks = math.ceil(total_max_hours / 10)
        return roadmap, estimated_weeks


# ---------------------------------------------------------------------------
# Tool 7 — Explanation Generator
# ---------------------------------------------------------------------------
class ExplanationGenerator:
    """Synthesises a human-readable report from scores + roadmap."""

    def generate(
        self,
        overall: float,
        skill_scores: list[SkillScore],
        strengths: list[str],
        gaps: list[str],
        estimated_weeks: int,
    ) -> str:
        lines = [
            f"📊 Overall Match Score: {overall:.0f}/100",
            "",
            f"✅ Strengths ({len(strengths)}):",
        ]
        for s in strengths:
            lines.append(f"   • {s}")

        lines += ["", f"🔧 Skill Gaps ({len(gaps)}):"]
        for g in gaps:
            lines.append(f"   • {g}")

        verdict = (
            "🟢 Strong fit — minor upskilling needed."
            if overall >= 70
            else "🟡 Moderate fit — focused learning can bridge the gap."
            if overall >= 45
            else "🔴 Significant gaps — structured learning plan recommended."
        )
        lines += [
            "",
            verdict,
            f"⏱  Estimated time to bridge gaps: ~{estimated_weeks} weeks (at 10 hrs/week)",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Master Agent
# ---------------------------------------------------------------------------
class CatalystAgent:
    """
    Orchestrates all tools in sequence:
      InputParser → SkillExtractor → EmbeddingEngine →
      ScoringEngine → RoadmapBuilder → ExplanationGenerator
    """

    def __init__(self):
        logger.info("Initialising CatalystAgent …")
        self.parser = InputParser()
        self.extractor = SkillExtractor()
        self.embedder = EmbeddingEngine()
        self.scorer = ScoringEngine(self.embedder)
        self.resource_finder = ResourceFinder()
        self.roadmap_builder = RoadmapBuilder(self.resource_finder)
        self.explainer = ExplanationGenerator()
        logger.info("CatalystAgent ready.")

    def run(self, resume_text: str, jd_text: str) -> AssessmentResult:
        """
        Main entry point.
        Returns an AssessmentResult dataclass with all computed fields.
        """
        if not resume_text.strip() or not jd_text.strip():
            raise ValueError("Resume and Job Description must not be empty.")

        # Step 1 — Parse
        parsed = self.parser.parse(resume_text, jd_text)

        # Step 2 — Extract skills
        jd_skills = self.extractor.extract(parsed["jd"], context="job description")
        resume_skills = self.extractor.extract(parsed["resume"], context="resume")

        if not jd_skills:
            raise ValueError("No skills could be extracted from the Job Description.")

        # Step 3 & 4 — Score
        skill_scores, overall = self.scorer.score_all(
            jd_skills, parsed["resume"], resume_skills
        )

        # Step 5 — Classify strengths / gaps
        strengths = [ss.skill for ss in skill_scores if ss.candidate_level == "strong"]
        gaps = [ss.skill for ss in skill_scores if ss.candidate_level != "strong"]

        # Step 6 — Build roadmap
        roadmap, estimated_weeks = self.roadmap_builder.build(skill_scores)

        # Step 7 — Explain
        explanation = self.explainer.generate(
            overall, skill_scores, strengths, gaps, estimated_weeks
        )

        result = AssessmentResult(
            overall_match_score=overall,
            skill_scores=skill_scores,
            strengths=strengths,
            gaps=gaps,
            learning_roadmap=roadmap,
            estimated_weeks=estimated_weeks,
            explanation=explanation,
            raw_jd_skills=jd_skills,
            raw_resume_skills=resume_skills,
        )
        logger.info("Assessment complete. Overall score: %.1f", overall)
        return result

    def to_json(self, result: AssessmentResult, indent: int = 2) -> str:
        """Serialise result to pretty JSON."""
        return json.dumps(result.to_dict(), indent=indent, default=str)


# ---------------------------------------------------------------------------
# Quick CLI smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    SAMPLE_JD = """
    We are looking for a Senior Data Scientist with 4+ years of experience.
    Must have: Python, Machine Learning, Deep Learning, SQL, Statistics, NLP.
    Nice to have: Docker, Kubernetes, AWS, Communication skills.
    Experience with PyTorch or TensorFlow required.
    """

    SAMPLE_RESUME = """
    John Doe — Data Scientist
    5 years experience in Python and data analysis.
    Worked with sklearn, pandas, numpy for machine learning projects.
    Basic knowledge of SQL and statistics.
    No cloud or container experience.
    Strong communication skills; presented findings to executives.
    """

    agent = CatalystAgent()
    result = agent.run(SAMPLE_RESUME, SAMPLE_JD)
    print(result.explanation)
    print("\n--- JSON Output (truncated) ---")
    print(agent.to_json(result)[:1000])