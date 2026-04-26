"""
Catalyst — Skill Assessment & Learning Plan Agent
Streamlit UI
============
Clean, modular interface for the Catalyst AI Agent.

Run:
    streamlit run streamlit_app.py
"""

import json
import time
import traceback

import streamlit as st

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Catalyst — Skill Assessment Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS — refined dark theme with amber accents
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

    /* ── base ── */
    html, body, [data-testid="stAppViewContainer"] {
        background: #0d0f14;
        color: #e8e6e1;
        font-family: 'DM Sans', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: #111318 !important;
        border-right: 1px solid #1e2230;
    }
    .block-container { padding-top: 2rem; max-width: 1200px; }

    /* ── typography ── */
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

    /* ── hero banner ── */
    .hero {
        background: linear-gradient(135deg, #0d0f14 0%, #12161f 50%, #0a0d12 100%);
        border: 1px solid #1e2230;
        border-radius: 16px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(245,158,11,0.12) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        color: #f5f0e8;
        margin: 0 0 0.3rem;
        letter-spacing: -0.5px;
    }
    .hero-sub {
        color: #7a8399;
        font-size: 1rem;
        margin: 0;
    }
    .hero-badge {
        display: inline-block;
        background: #f59e0b22;
        border: 1px solid #f59e0b44;
        color: #f59e0b;
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 0.8rem;
        letter-spacing: 0.5px;
    }

    /* ── metric cards ── */
    .metric-row { display: flex; gap: 1rem; margin: 1.5rem 0; flex-wrap: wrap; }
    .metric-card {
        background: #111318;
        border: 1px solid #1e2230;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        flex: 1;
        min-width: 160px;
    }
    .metric-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.7rem;
        color: #5a6378;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #f5f0e8;
        line-height: 1;
    }
    .metric-unit { font-size: 1rem; color: #7a8399; }

    /* ── score dial colours ── */
    .score-high  { color: #34d399; }
    .score-mid   { color: #f59e0b; }
    .score-low   { color: #f87171; }

    /* ── skill pills ── */
    .pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 0.5rem 0 1rem; }
    .pill {
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid;
    }
    .pill-strong { background: #06402655; border-color: #34d39944; color: #6ee7b7; }
    .pill-partial { background: #78350f55; border-color: #f59e0b44; color: #fcd34d; }
    .pill-missing { background: #7f1d1d55; border-color: #f8717144; color: #fca5a5; }
    .pill-neutral { background: #1e223055; border-color: #2a3045; color: #7a8399; }

    /* ── roadmap cards ── */
    .roadmap-card {
        background: #111318;
        border: 1px solid #1e2230;
        border-left: 3px solid #f59e0b;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .roadmap-card.high { border-left-color: #f87171; }
    .roadmap-card.medium { border-left-color: #f59e0b; }
    .roadmap-card.low { border-left-color: #34d399; }
    .roadmap-title {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: #f5f0e8;
        margin-bottom: 0.4rem;
    }
    .roadmap-meta {
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        color: #5a6378;
        margin-bottom: 0.7rem;
    }
    .roadmap-milestone {
        font-size: 0.85rem;
        color: #9aa3b8;
        margin-bottom: 0.7rem;
        padding: 0.5rem 0.8rem;
        background: #0d0f1480;
        border-radius: 6px;
    }
    .resource-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        color: #93c5fd;
        text-decoration: none;
        margin-right: 10px;
        margin-bottom: 4px;
    }

    /* ── section headers ── */
    .section-header {
        font-family: 'Syne', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #f5f0e8;
        margin: 1.5rem 0 0.8rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── score bar ── */
    .score-bar-bg {
        background: #1e2230;
        border-radius: 6px;
        height: 8px;
        margin: 4px 0 8px;
        overflow: hidden;
    }
    .score-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }

    /* ── explanation box ── */
    .explanation-box {
        background: #111318;
        border: 1px solid #1e2230;
        border-radius: 12px;
        padding: 1.5rem;
        font-family: 'DM Mono', monospace;
        font-size: 0.82rem;
        line-height: 1.8;
        color: #9aa3b8;
        white-space: pre-wrap;
    }

    /* ── buttons ── */
    div.stButton > button {
        background: #f59e0b !important;
        color: #0d0f14 !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
        letter-spacing: 0.3px;
        transition: opacity 0.2s;
    }
    div.stButton > button:hover { opacity: 0.88 !important; }

    /* ── text areas & inputs ── */
    textarea, .stTextArea textarea {
        background: #111318 !important;
        border: 1px solid #1e2230 !important;
        border-radius: 8px !important;
        color: #e8e6e1 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    textarea:focus { border-color: #f59e0b66 !important; }

    /* ── tabs ── */
    [data-testid="stTabs"] button {
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        color: #5a6378 !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #f59e0b !important;
        border-bottom-color: #f59e0b !important;
    }

    /* ── divider ── */
    hr { border-color: #1e2230; }

    /* chat bubbles */
    .chat-user {
        background: #1e2230;
        border-radius: 12px 12px 4px 12px;
        padding: 0.8rem 1.1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #e8e6e1;
        margin-left: 20%;
    }
    .chat-agent {
        background: #111318;
        border: 1px solid #1e2230;
        border-radius: 12px 12px 12px 4px;
        padding: 0.8rem 1.1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #9aa3b8;
        margin-right: 20%;
        font-family: 'DM Mono', monospace;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
def init_session():
    defaults = {
        "result": None,
        "result_json": None,
        "agent": None,
        "chat_history": [],
        "analysis_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ---------------------------------------------------------------------------
# Lazy-load agent (avoids reloading model on every rerun)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_agent():
    """Load once, reuse across sessions."""
    from catalyst_agent import CatalystAgent
    return CatalystAgent()


# ---------------------------------------------------------------------------
# Helper: render a horizontal score bar
# ---------------------------------------------------------------------------
def score_bar(score: float):
    colour = "#34d399" if score >= 65 else "#f59e0b" if score >= 35 else "#f87171"
    st.markdown(
        f"""
        <div class="score-bar-bg">
          <div class="score-bar-fill" style="width:{score}%; background:{colour};"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Helper: render roadmap card
# ---------------------------------------------------------------------------
def render_roadmap_card(item, idx: int):
    priority_colour = {"high": "high", "medium": "medium", "low": "low"}.get(item["priority"], "medium")
    type_icons = {"video": "▶", "course": "📚", "docs": "📄", "interactive": "🎮"}
    lo, hi = item["estimated_hours"]

    resource_links = " ".join(
        f'<a class="resource-link" href="{r["url"]}" target="_blank">'
        f'{type_icons.get(r["resource_type"], "🔗")} {r["title"]}</a>'
        for r in item["resources"][:3]
    )

    st.markdown(
        f"""
        <div class="roadmap-card {priority_colour}">
            <div class="roadmap-title">#{idx} {item['skill'].title()}</div>
            <div class="roadmap-meta">
                PRIORITY: {item['priority'].upper()} &nbsp;|&nbsp;
                EST. TIME: {lo}–{hi} hrs
            </div>
            <div class="roadmap-milestone">🎯 Milestone: {item['milestone']}</div>
            <div>{resource_links}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;color:#f5f0e8;margin-bottom:0.3rem;">⚡ Catalyst</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div style="font-size:0.8rem;color:#5a6378;margin-bottom:1.5rem;">Skill Assessment Agent v1.0</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("**How it works**")
    steps = [
        ("1", "Paste your Resume"),
        ("2", "Paste the Job Description"),
        ("3", "Click Analyse"),
        ("4", "Get your personalised roadmap"),
    ]
    for num, label in steps:
        st.markdown(
            f'<div style="display:flex;gap:10px;align-items:center;margin-bottom:8px;">'
            f'<span style="background:#f59e0b22;color:#f59e0b;border-radius:50%;width:22px;height:22px;'
            f'display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-family:DM Mono,monospace;flex-shrink:0;">{num}</span>'
            f'<span style="font-size:0.85rem;color:#9aa3b8;">{label}</span></div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("**Tech Stack**")
    for tech in ["sentence-transformers", "HuggingFace (free)", "Streamlit", "Python 3.10+"]:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:0.75rem;color:#5a6378;margin-bottom:4px;">▸ {tech}</div>', unsafe_allow_html=True)

    st.divider()
    if st.session_state.analysis_done and st.session_state.result_json:
        st.download_button(
            label="⬇ Download JSON Report",
            data=st.session_state.result_json,
            file_name="catalyst_assessment.json",
            mime="application/json",
        )

    if st.button("🔄 Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">AI-POWERED · FREE TIER · OPEN SOURCE</div>
        <div class="hero-title">Skill Assessment Agent</div>
        <p class="hero-sub">Drop your resume + job description. Get a personalised skill gap analysis and learning roadmap — instantly.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Main tabs
# ---------------------------------------------------------------------------
tab_input, tab_results, tab_chat = st.tabs(["📥 Input", "📊 Results", "💬 Chat with Agent"])

# ---------------------------------------------------------------------------
# File text extraction helpers
# ---------------------------------------------------------------------------
def extract_text_from_file(uploaded_file) -> tuple[str, str]:
    """
    Extract plain text from an uploaded file.
    Supports: PDF, DOCX, TXT, MD
    Returns (extracted_text, error_message).  error_message is "" on success.
    """
    name = uploaded_file.name.lower()
    raw_bytes = uploaded_file.read()

    # ── TXT / MD ──────────────────────────────────────────────────────────
    if name.endswith((".txt", ".md")):
        try:
            return raw_bytes.decode("utf-8", errors="replace"), ""
        except Exception as e:
            return "", f"Could not read text file: {e}"

    # ── PDF ───────────────────────────────────────────────────────────────
    if name.endswith(".pdf"):
        try:
            import io
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(raw_bytes))
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())
            if not pages:
                return "", "PDF appears to be scanned/image-based — no extractable text found. Please paste text manually."
            return "\n\n".join(pages), ""
        except ImportError:
            return "", "pypdf not installed. Run: pip install pypdf"
        except Exception as e:
            return "", f"PDF extraction failed: {e}"

    # ── DOCX ──────────────────────────────────────────────────────────────
    if name.endswith(".docx"):
        try:
            import io
            from docx import Document
            doc = Document(io.BytesIO(raw_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            if not paragraphs:
                return "", "DOCX file appears empty."
            return "\n".join(paragraphs), ""
        except ImportError:
            return "", "python-docx not installed. Run: pip install python-docx"
        except Exception as e:
            return "", f"DOCX extraction failed: {e}"

    # ── DOC (legacy) ──────────────────────────────────────────────────────
    if name.endswith(".doc"):
        return "", "Legacy .doc format is not supported. Please save as .docx or .pdf and re-upload."

    return "", f"Unsupported file type: {uploaded_file.name.split('.')[-1].upper()}"


def file_upload_zone(label: str, key_prefix: str, icon: str) -> str:
    """
    Renders a dual-mode input zone (Upload File tab + Paste Text tab).
    Returns the final resolved text string.
    """
    ACCEPTED = ["pdf", "docx", "txt", "md"]

    st.markdown(f'<div class="section-header">{icon} {label}</div>', unsafe_allow_html=True)

    mode_upload, mode_paste = st.tabs([f"📎 Upload File", f"✏️ Paste Text"])

    extracted_from_file = ""
    file_info = ""

    with mode_upload:
        st.markdown(
            '<div style="font-size:0.8rem;color:#5a6378;margin-bottom:0.6rem;">'
            'Supported formats: <code style="background:#1e2230;padding:2px 6px;border-radius:4px;color:#f59e0b;">PDF</code> '
            '<code style="background:#1e2230;padding:2px 6px;border-radius:4px;color:#f59e0b;">DOCX</code> '
            '<code style="background:#1e2230;padding:2px 6px;border-radius:4px;color:#f59e0b;">TXT</code> '
            '<code style="background:#1e2230;padding:2px 6px;border-radius:4px;color:#f59e0b;">MD</code>'
            '</div>',
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            f"upload_{key_prefix}",
            type=ACCEPTED,
            label_visibility="collapsed",
            key=f"uploader_{key_prefix}",
        )

        if uploaded:
            with st.spinner(f"📖 Reading {uploaded.name}…"):
                text, err = extract_text_from_file(uploaded)

            if err:
                st.error(f"⚠️ {err}")
            else:
                extracted_from_file = text
                word_count = len(text.split())
                char_count = len(text)
                file_info = uploaded.name
                st.markdown(
                    f'<div style="background:#06402620;border:1px solid #34d39930;border-radius:8px;'
                    f'padding:0.6rem 1rem;font-size:0.8rem;color:#6ee7b7;margin-top:0.5rem;">'
                    f'✅ <strong>{uploaded.name}</strong> extracted successfully — '
                    f'{word_count:,} words · {char_count:,} chars</div>',
                    unsafe_allow_html=True,
                )
                # Show a collapsible preview
                with st.expander("👁 Preview extracted text", expanded=False):
                    st.text_area(
                        "preview",
                        value=text[:2000] + ("…" if len(text) > 2000 else ""),
                        height=160,
                        disabled=True,
                        label_visibility="collapsed",
                    )

    with mode_paste:
        placeholder_map = {
            "resume": (
                "Paste your resume here…\n\n"
                "Example:\nJane Smith — Software Engineer\n"
                "4 years experience in Python, React, REST APIs, PostgreSQL, Git.\n"
                "Basic Docker exposure. Strong communication skills."
            ),
            "jd": (
                "Paste the job description here…\n\n"
                "Example:\nSenior Full-Stack Engineer\n"
                "Required: Python, React, Node.js, SQL, Docker, AWS, Git.\n"
                "Nice to have: Kubernetes, TypeScript, Agile/Scrum."
            ),
        }
        pasted = st.text_area(
            f"paste_{key_prefix}",
            value=st.session_state.get(f"pasted_{key_prefix}", ""),
            height=200,
            label_visibility="collapsed",
            placeholder=placeholder_map.get(key_prefix, "Paste text here…"),
            key=f"paste_area_{key_prefix}",
        )
        if pasted.strip():
            st.markdown(
                f'<div style="font-family:DM Mono,monospace;font-size:0.7rem;color:#3a4055;text-align:right;margin-top:-8px;">'
                f'{len(pasted):,} chars · {len(pasted.split()):,} words</div>',
                unsafe_allow_html=True,
            )

    # Priority: file upload wins if present, else paste
    final_text = extracted_from_file if extracted_from_file.strip() else (pasted if "pasted" not in dir() else pasted)

    # Source badge
    if extracted_from_file.strip():
        st.markdown(
            f'<div style="font-size:0.75rem;color:#5a6378;margin-top:4px;">'
            f'📎 Using: <span style="color:#f59e0b;">{file_info}</span></div>',
            unsafe_allow_html=True,
        )
    elif final_text.strip():
        st.markdown(
            '<div style="font-size:0.75rem;color:#5a6378;margin-top:4px;">✏️ Using: pasted text</div>',
            unsafe_allow_html=True,
        )

    return final_text


# ── TAB 1: INPUT ──────────────────────────────────────────────────────────
with tab_input:

    # ── Top info banner
    st.markdown(
        '<div style="background:#111318;border:1px solid #1e2230;border-left:3px solid #f59e0b;'
        'border-radius:8px;padding:0.75rem 1.1rem;font-size:0.82rem;color:#7a8399;margin-bottom:1.2rem;">'
        '💡 <strong style="color:#f5f0e8;">Two ways to input:</strong> '
        'Upload a <strong style="color:#f5f0e8;">PDF / DOCX / TXT</strong> file directly, '
        'or switch to the <strong style="color:#f5f0e8;">Paste Text</strong> tab to type/paste manually. '
        'File upload takes priority if both are provided.</div>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        resume_text = file_upload_zone("Resume / CV", "resume", "📄")

    with col_right:
        jd_text = file_upload_zone("Job Description", "jd", "💼")

    st.markdown("<hr style='border-color:#1e2230;margin:1.5rem 0;'>", unsafe_allow_html=True)

    # ── Readiness status row
    resume_ready = len(resume_text.strip()) >= 30
    jd_ready = len(jd_text.strip()) >= 30
    both_ready = resume_ready and jd_ready

    status_html = (
        '<div style="display:flex;gap:2rem;justify-content:center;margin-bottom:1.2rem;flex-wrap:wrap;">'
    )
    for label, ready in [("Resume", resume_ready), ("Job Description", jd_ready)]:
        colour = "#34d399" if ready else "#3a4055"
        icon = "✅" if ready else "⬜"
        msg = "Ready" if ready else "Not yet provided"
        status_html += (
            f'<div style="display:flex;align-items:center;gap:8px;font-size:0.85rem;">'
            f'<span>{icon}</span>'
            f'<span style="color:{colour};font-weight:600;">{label}</span>'
            f'<span style="color:#3a4055;font-family:DM Mono,monospace;font-size:0.75rem;">— {msg}</span>'
            f'</div>'
        )
    status_html += "</div>"
    st.markdown(status_html, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_button = st.button(
            "⚡ Analyse Skills & Generate Roadmap",
            disabled=not both_ready,
        )
        if not both_ready:
            missing = []
            if not resume_ready:
                missing.append("Resume")
            if not jd_ready:
                missing.append("Job Description")
            st.markdown(
                f'<div style="text-align:center;font-size:0.78rem;color:#3a4055;margin-top:6px;">'
                f'Still needed: {" & ".join(missing)}</div>',
                unsafe_allow_html=True,
            )

    if run_button:
        if not resume_text.strip() or not jd_text.strip():
            st.error("Please provide both Resume and Job Description.")
        else:
            with st.spinner("🔍 Loading AI models and analysing…"):
                try:
                    t0 = time.time()
                    agent = load_agent()
                    result = agent.run(resume_text, jd_text)
                    elapsed = time.time() - t0

                    st.session_state.result = result.to_dict()
                    st.session_state.result_json = agent.to_json(result)
                    st.session_state.analysis_done = True
                    st.success(f"✅ Analysis complete in {elapsed:.1f}s — switch to the Results tab!")
                except ValueError as ve:
                    st.error(f"Input error: {ve}")
                except Exception:
                    st.error("Unexpected error during analysis. See details below.")
                    st.code(traceback.format_exc())


# ── TAB 2: RESULTS ────────────────────────────────────────────────────────
with tab_results:
    if not st.session_state.analysis_done:
        st.markdown(
            '<div style="text-align:center;padding:4rem 2rem;color:#3a4055;">'
            '<div style="font-size:3rem;margin-bottom:1rem;">⚡</div>'
            '<div style="font-family:Syne,sans-serif;font-size:1.2rem;">Run the analysis first</div>'
            '<div style="font-size:0.85rem;margin-top:0.5rem;">Head to the Input tab and click Analyse</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        r = st.session_state.result
        overall = r["overall_match_score"]
        score_class = "score-high" if overall >= 65 else "score-mid" if overall >= 40 else "score-low"

        # ── Overview metrics
        st.markdown('<div class="section-header">📊 Overview</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-label">Overall Match</div>
                    <div class="metric-value {score_class}">{overall:.0f}<span class="metric-unit">/100</span></div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Skills Matched</div>
                    <div class="metric-value">{len(r['strengths'])}<span class="metric-unit"> skills</span></div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Skill Gaps</div>
                    <div class="metric-value score-low">{len(r['gaps'])}<span class="metric-unit"> skills</span></div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Est. Upskill Time</div>
                    <div class="metric-value">{r['estimated_weeks']}<span class="metric-unit"> wks</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Verdict explanation
        st.markdown('<div class="section-header">📝 Assessment Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="explanation-box">{r["explanation"]}</div>', unsafe_allow_html=True)

        # ── Skill breakdown
        st.markdown('<div class="section-header">🔬 Skill-by-Skill Breakdown</div>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        skill_scores = r["skill_scores"]
        mid = len(skill_scores) // 2 + len(skill_scores) % 2

        for col, chunk in [(col_a, skill_scores[:mid]), (col_b, skill_scores[mid:])]:
            with col:
                for ss in chunk:
                    pill_class = (
                        "pill-strong" if ss["candidate_level"] == "strong"
                        else "pill-partial" if ss["candidate_level"] == "partial"
                        else "pill-missing"
                    )
                    icon = "✅" if ss["candidate_level"] == "strong" else "⚠️" if ss["candidate_level"] == "partial" else "❌"
                    label = "CORE" if ss["required_level"] == "core" else "OPTIONAL"
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;">'
                        f'<span style="font-size:0.85rem;color:#c5c0b8;">{icon} {ss["skill"].title()}</span>'
                        f'<span style="font-family:DM Mono,monospace;font-size:0.72rem;color:#5a6378;">'
                        f'{label} · {ss["score"]:.0f}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    score_bar(ss["score"])

        # ── Strengths & Gaps pills
        col_s, col_g = st.columns(2)
        with col_s:
            st.markdown('<div class="section-header">✅ Strengths</div>', unsafe_allow_html=True)
            pills_html = '<div class="pill-row">' + "".join(
                f'<span class="pill pill-strong">{s.title()}</span>' for s in r["strengths"]
            ) + "</div>"
            st.markdown(pills_html or "None detected.", unsafe_allow_html=True)
        with col_g:
            st.markdown('<div class="section-header">🔧 Skill Gaps</div>', unsafe_allow_html=True)
            pills_html = '<div class="pill-row">' + "".join(
                f'<span class="pill pill-missing">{g.title()}</span>' for g in r["gaps"]
            ) + "</div>"
            st.markdown(pills_html or "No significant gaps!", unsafe_allow_html=True)

        # ── Learning Roadmap
        st.markdown('<div class="section-header">🗺️ Personalised Learning Roadmap</div>', unsafe_allow_html=True)
        if not r["learning_roadmap"]:
            st.success("🎉 No significant gaps found — you're a great match!")
        else:
            priority_order = {"high": 0, "medium": 1, "low": 2}
            roadmap_sorted = sorted(r["learning_roadmap"], key=lambda x: priority_order.get(x["priority"], 3))
            for idx, item in enumerate(roadmap_sorted, 1):
                render_roadmap_card(item, idx)

        # ── JSON download inline
        st.markdown('<div class="section-header">📦 Raw JSON Output</div>', unsafe_allow_html=True)
        with st.expander("Show / hide JSON", expanded=False):
            st.code(st.session_state.result_json, language="json")


# ── TAB 3: CHAT ───────────────────────────────────────────────────────────
with tab_chat:
    st.markdown('<div class="section-header">💬 Ask the Agent</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.85rem;color:#5a6378;margin-bottom:1rem;">'
        'Ask follow-up questions about your assessment, learning resources, or career advice.</div>',
        unsafe_allow_html=True,
    )

    # Render chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-agent">⚡ {msg["content"]}</div>', unsafe_allow_html=True)

    user_q = st.text_area("Your question:", height=80, label_visibility="collapsed", placeholder="e.g. How long will it take to learn Docker?")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        send_btn = st.button("Send →")

    if send_btn and user_q.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_q})

        # Build a lightweight context-aware response using assessment data
        r = st.session_state.result or {}
        overall = r.get("overall_match_score", "N/A")
        strengths = r.get("strengths", [])
        gaps = r.get("gaps", [])
        weeks = r.get("estimated_weeks", "N/A")

        q_lower = user_q.lower()

        # Rule-based smart responses (no API needed for chat)
        if any(kw in q_lower for kw in ["how long", "time", "weeks", "months", "duration"]):
            answer = (
                f"Based on your assessment, bridging your skill gaps will take approximately "
                f"**{weeks} weeks** at ~10 hrs/week of focused study. "
                f"Your biggest time investments will be in: {', '.join(gaps[:3]) if gaps else 'no major gaps identified'}."
            )
        elif any(kw in q_lower for kw in ["strong", "strength", "good at", "best"]):
            answer = (
                f"Your strongest skills are: **{', '.join(strengths[:5]) if strengths else 'not yet analysed'}**. "
                f"These directly match the job requirements and give you a solid foundation."
            )
        elif any(kw in q_lower for kw in ["gap", "missing", "lack", "need to learn", "improve"]):
            answer = (
                f"Your key skill gaps are: **{', '.join(gaps[:5]) if gaps else 'none identified'}**. "
                f"Focus on high-priority ones first — check the Roadmap tab for curated free resources."
            )
        elif any(kw in q_lower for kw in ["score", "match", "result", "percentage"]):
            answer = (
                f"Your overall match score is **{overall}/100**. "
                + ("You're a strong candidate — minor polish needed." if isinstance(overall, (int, float)) and overall >= 70
                   else "Focused upskilling can significantly improve your fit." if isinstance(overall, (int, float)) and overall >= 45
                   else "A structured learning plan is recommended to bridge gaps.")
            )
        elif any(kw in q_lower for kw in ["resource", "where", "learn", "course", "youtube", "free"]):
            roadmap = r.get("learning_roadmap", [])
            if roadmap:
                top = roadmap[0]
                res_names = [res["title"] for res in top.get("resources", [])[:2]]
                answer = (
                    f"For **{top['skill'].title()}** (your highest priority), I recommend: "
                    + "; ".join(res_names)
                    + ". Check the Roadmap tab for the full list!"
                )
            else:
                answer = "Run the analysis first to get personalised resource recommendations."
        elif any(kw in q_lower for kw in ["download", "export", "json", "save"]):
            answer = "Click the **⬇ Download JSON Report** button in the left sidebar to save your full assessment report."
        elif not r:
            answer = "Please run the analysis first (Input tab → Analyse button) so I can answer questions about your specific assessment."
        else:
            # Generic helpful response
            answer = (
                f"Great question! Based on your assessment (score: {overall}/100), "
                f"you match well on {', '.join(strengths[:2]) if strengths else 'several skills'} "
                f"but have opportunities to grow in {', '.join(gaps[:2]) if gaps else 'a few areas'}. "
                f"The Roadmap tab has your personalised learning plan. What specific aspect would you like to explore?"
            )

        st.session_state.chat_history.append({"role": "agent", "content": answer})
        st.rerun()