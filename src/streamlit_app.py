"""Streamlit demo UI — a thin, polished presentation entry point.

A third entry point alongside `main.py`. It owns presentation and path
provisioning ("where") and reuses `pipeline.run()` unchanged ("what order").
It contains NO business logic: it reuses `pipeline.run()` for extraction and
`load_brain_dump()` only to display the source text for a before/after view,
and never reimplements a stage.

This module is styling + layout only (CSS and HTML string builders around the
existing pipeline). Nothing here changes the pipeline, prompts, or model.

Run:  streamlit run src/streamlit_app.py
"""

from __future__ import annotations

import html
import json
import tempfile
from pathlib import Path

import streamlit as st

from career_engine.ingestion.loader import load_brain_dump
from career_engine.llm_client import LLMError
from career_engine.pipeline import run

# --- Static presentation assets ---------------------------------------------

# Temporary lightweight brand mark (placeholder until the official logo exists):
# a rounded frame with an ascending 3-node path — geometric, monoline, outline
# only, evoking raw input → structured knowledge. Linear/Notion-style.
BRAND_MARK_SVG = (
    "<svg width='44' height='44' viewBox='0 0 48 48' fill='none' "
    "stroke='#2F8F6E' stroke-width='2.2' stroke-linecap='round' "
    "stroke-linejoin='round'>"
    "<rect x='6' y='6' width='36' height='36' rx='12'/>"
    "<path d='M14 34 L24 24 L34 14'/>"
    "<circle cx='14' cy='34' r='2.6'/>"
    "<circle cx='24' cy='24' r='2.6'/>"
    "<circle cx='34' cy='14' r='2.6'/></svg>"
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{
  --bg:#F7F7F5; --card:#FFFFFF; --border:#EAEAE7; --text:#201F1D;
  --muted:#75736E; --accent:#2F8F6E; --accent-soft:#EAF4EF; --radius:16px;
  --shadow:0 1px 2px rgba(16,15,14,.04),0 6px 22px rgba(16,15,14,.05);
}
html,body,[class*="css"]{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}
.stApp{background:var(--bg);}
.block-container{max-width:1180px;padding-top:2.2rem;padding-bottom:2rem;}
#MainMenu,[data-testid="stToolbar"]{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}

.cef-header{text-align:center;margin-bottom:1.3rem;}
.cef-header .cef-mark{margin-bottom:.4rem;}
.cef-title{font-size:2.05rem;font-weight:700;letter-spacing:-0.02em;color:var(--text);margin:0;}
.cef-sub{font-size:1rem;color:var(--muted);margin-top:.4rem;}

.cef-success{text-align:center;color:var(--accent);font-size:.9rem;font-weight:600;
  margin:.1rem 0 1.3rem;display:flex;align-items:center;justify-content:center;gap:.4rem;}

.cef-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);
  box-shadow:var(--shadow);padding:1.2rem 1.35rem;}
.cef-card-title{font-size:1.02rem;font-weight:600;color:var(--text);margin:0 0 .9rem;
  display:flex;align-items:center;gap:.5rem;}
.cef-scroll{height:52vh;overflow-y:auto;padding-right:.6rem;}
.cef-scroll::-webkit-scrollbar{width:8px;}
.cef-scroll::-webkit-scrollbar-thumb{background:#E0E0DC;border-radius:8px;}
.cef-doc{white-space:pre-wrap;font-size:.92rem;line-height:1.75;color:#33322f;}

.cef-section{background:#FBFBFA;border:1px solid var(--border);border-radius:12px;
  padding:.85rem 1rem;margin-bottom:.8rem;}
.cef-section-h{font-size:.72rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;
  color:var(--accent);margin:0 0 .55rem;}
.cef-field{font-size:.92rem;margin:.2rem 0;color:var(--text);}
.cef-field .k{color:var(--muted);}
.cef-chip{display:inline-block;background:var(--accent-soft);color:var(--accent);border-radius:999px;
  padding:.22rem .62rem;margin:.18rem .3rem .18rem 0;font-size:.82rem;font-weight:500;}
.cef-ach{border-left:2px solid var(--accent);padding-left:.75rem;margin:.55rem 0;}
.cef-ach-t{font-weight:600;font-size:.92rem;color:var(--text);}
.cef-ach-m{font-size:.85rem;color:var(--muted);margin-top:.1rem;}
.cef-empty{color:var(--muted);font-style:italic;font-size:.9rem;}

.stButton>button{background:var(--accent);color:#fff;border:none;border-radius:10px;
  padding:.5rem 1.15rem;font-weight:600;box-shadow:none;transition:background .15s ease;}
.stButton>button:hover{background:#277a5e;color:#fff;}
.stButton>button:disabled{background:#DBE7E1;color:#fff;}
[data-testid="stFileUploaderDropzone"]{border-radius:12px;border:1px dashed var(--border);background:var(--card);}

.cef-footer{text-align:center;color:var(--muted);font-size:.8rem;margin-top:1.6rem;
  display:flex;align-items:center;justify-content:center;gap:.5rem;}
.cef-badge{background:var(--accent-soft);color:var(--accent);border-radius:999px;
  padding:.15rem .62rem;font-weight:600;}
</style>
"""

HEADER_HTML = (
    f"<div class='cef-header'><div class='cef-mark'>{BRAND_MARK_SVG}</div>"
    "<h1 class='cef-title'>Career Engineering Framework</h1>"
    "<div class='cef-sub'>Turn an unstructured career brain dump into a "
    "structured Career Profile — powered by AI.</div></div>"
)

FOOTER_HTML = (
    "<div class='cef-footer'><span class='cef-badge'>Sprint 1 · MVP</span>"
    "<span>Career Engineering Framework</span></div>"
)


# --- HTML builders (presentation only) --------------------------------------

def brain_dump_card_html(text: str | None) -> str:
    if text:
        body = f"<div class='cef-scroll cef-doc'>{html.escape(text)}</div>"
    else:
        body = (
            "<div class='cef-scroll cef-doc'><span class='cef-empty'>Upload a "
            ".docx and extract to see the source text here.</span></div>"
        )
    return f"<div class='cef-card'><div class='cef-card-title'>📄 Brain Dump</div>{body}</div>"


def profile_card_html(data: dict | None) -> str:
    esc = html.escape
    if data is None:
        body = (
            "<div class='cef-scroll'><span class='cef-empty'>The extracted "
            "Career Profile will appear here.</span></div>"
        )
        return f"<div class='cef-card'><div class='cef-card-title'>👤 Career Profile</div>{body}</div>"

    meta = data.get("metadata", {}) or {}
    roles = meta.get("target_roles") or []

    def field(label: str, value: str) -> str:
        return f"<div class='cef-field'><span class='k'>{esc(label)}:</span> {esc(value) if value else '—'}</div>"

    meta_html = (
        field("Name", meta.get("name", ""))
        + field("Headline", meta.get("headline", ""))
        + field("Location", meta.get("location", ""))
        + field("Email", meta.get("email", ""))
        + field("Summary", meta.get("summary", ""))
        + "<div class='cef-field'><span class='k'>Target Roles:</span></div>"
        + ("".join(f"<span class='cef-chip'>{esc(r)}</span>" for r in roles)
           or "<span class='cef-empty'>—</span>")
    )

    skills = data.get("skills") or []
    if skills:
        skills_html = "".join(
            "<span class='cef-chip'>"
            + esc(s.get("name", ""))
            + (f" · {esc(s.get('category'))}" if s.get("category") else "")
            + "</span>"
            for s in skills
        )
    else:
        skills_html = "<span class='cef-empty'>No skills extracted.</span>"

    achievements = data.get("achievements") or []
    if achievements:
        parts = []
        for a in achievements:
            meta_bits = []
            if a.get("context"):
                meta_bits.append(f"Context: {esc(a['context'])}")
            if a.get("impact"):
                meta_bits.append(f"Impact: {esc(a['impact'])}")
            line = f"<div class='cef-ach-m'>{' · '.join(meta_bits)}</div>" if meta_bits else ""
            parts.append(
                f"<div class='cef-ach'><div class='cef-ach-t'>{esc(a.get('title', ''))}</div>{line}</div>"
            )
        ach_html = "".join(parts)
    else:
        ach_html = "<span class='cef-empty'>No achievements extracted.</span>"

    stories = data.get("hero_stories") or []
    if stories:
        parts = []
        for h in stories:
            rows = ""
            for label, key in (("Situation", "situation"), ("Action", "action"), ("Result", "result")):
                if h.get(key):
                    rows += f"<div class='cef-ach-m'><strong>{label}:</strong> {esc(h[key])}</div>"
            parts.append(
                f"<div class='cef-ach'><div class='cef-ach-t'>{esc(h.get('title') or 'Story')}</div>{rows}</div>"
            )
        hero_html = "".join(parts)
    else:
        hero_html = "<span class='cef-empty'>No hero stories were found in this Brain Dump yet.</span>"

    body = (
        "<div class='cef-scroll'>"
        f"<div class='cef-section'><div class='cef-section-h'>Metadata</div>{meta_html}</div>"
        f"<div class='cef-section'><div class='cef-section-h'>Skills</div>{skills_html}</div>"
        f"<div class='cef-section'><div class='cef-section-h'>Achievements</div>{ach_html}</div>"
        f"<div class='cef-section'><div class='cef-section-h'>Hero Stories</div>{hero_html}</div>"
        "</div>"
    )
    return f"<div class='cef-card'><div class='cef-card-title'>👤 Career Profile</div>{body}</div>"


# --- Page -------------------------------------------------------------------

st.set_page_config(
    page_title="Career Engineering Framework — MVP demo",
    page_icon="🪴",
    layout="wide",
)
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(HEADER_HTML, unsafe_allow_html=True)

_, controls, _ = st.columns([1, 2, 1])
with controls:
    uploaded = st.file_uploader("Brain Dump (.docx)", type=["docx"])
    clicked = st.button(
        "Extract Career Profile",
        type="primary",
        use_container_width=True,
        disabled=uploaded is None,
    )

# --- Orchestration delegated to the existing loader + pipeline --------------
brain_dump_text = None
profile_data = None
error_msg = None

if clicked and uploaded is not None:
    try:
        with st.spinner("Extracting…"):
            with tempfile.TemporaryDirectory() as tmp:
                tmp_dir = Path(tmp)
                input_path = tmp_dir / uploaded.name
                output_path = tmp_dir / "career_profile.json"

                input_path.write_bytes(uploaded.getvalue())
                # Reuse the existing loader for the "before" preview; the
                # pipeline loads the file again internally for extraction.
                brain_dump_text = load_brain_dump(input_path)
                run(input_path, output_path)
                profile_data = json.loads(output_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, LLMError) as exc:
        error_msg = f"Error: {exc}"

# --- Presentation -----------------------------------------------------------
if profile_data is not None:
    st.markdown(
        "<div class='cef-success'>✓ Career Profile extracted successfully.</div>",
        unsafe_allow_html=True,
    )

if error_msg:
    _, err, _ = st.columns([1, 2, 1])
    with err:
        st.error(error_msg)

left, right = st.columns(2)
with left:
    st.markdown(brain_dump_card_html(brain_dump_text), unsafe_allow_html=True)
with right:
    st.markdown(profile_card_html(profile_data), unsafe_allow_html=True)

st.markdown(FOOTER_HTML, unsafe_allow_html=True)
