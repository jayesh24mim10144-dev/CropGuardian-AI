import os
import sys

# Add project root and app directory to sys.path so imports resolve correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
app_dir = os.path.abspath(os.path.dirname(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

import streamlit as st
from dotenv import load_dotenv
from src.utils.logger import log_environment_snapshot, cleanup_temp_files
from src.services.knowledge_base.kb_manager import KnowledgeBaseManager

# Import UI modular components
from ui import init_page, render_header, render_footer, render_status_panel

load_dotenv()

# Initialize Page (Sets config, session states, styles, and renders sidebar)
init_page(title="CropGuardian AI", icon="🌿")

# Log Environment on startup and cleanup temp files (once per session only)
if "_startup_done" not in st.session_state:
    log_environment_snapshot()
    cleanup_temp_files(max_age_hours=24)
    st.session_state["_startup_done"] = True

# Initialize and validate Knowledge Base on application startup
if "kb_manager" not in st.session_state:
    try:
        st.session_state["kb_manager"] = KnowledgeBaseManager(validate_on_startup=True)
    except Exception as e:
        st.error(f"Critical Error: Failed to initialize Knowledge Base. {e}")
        st.stop()

# ─── Hero Section & Status Bar ────────────────────────────────────────────────
render_header(
    title="🌱 CropGuardian AI",
    subtitle="Instant Crop Disease Diagnosis & Farmer Advisory System",
    show_metrics=st.session_state.get("dev_mode", False),
)

# ─── Platform Capabilities — compact stat row ────────────────────────────────
st.markdown("### Platform Capabilities")

sc1, sc2, sc3, sc4 = st.columns(4, gap="medium")
for col, (num, lbl) in zip(
    [sc1, sc2, sc3, sc4],
    [("38", "Disease Classes"), ("14", "Crop Species"), ("5", "AI Agents"), ("2", "Orchestrators")],
):
    with col:
        with st.container(border=True):
            st.markdown(
                f'<div class="cg-stat-card">'
                f'<div class="cg-stat-num">{num}</div>'
                f'<div class="cg-stat-lbl">{lbl}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ─── How It Works — numbered 5-step flow ──────────────────────────────────────
st.markdown("### How It Works")

steps = [
    ("📷", "Upload Image",    "Upload a crop leaf photo to start."),
    ("🤖", "AI Detection",    "Disease classified with confidence scoring."),
    ("🌦️", "Weather Metrics", "Real-time farm weather fetched."),
    ("⚠️", "Risk Evaluation", "Fungal, bacterial & heat-stress risk."),
    ("💊", "Gemini Advisory", "Personalised treatment plan generated."),
]

# Row 1 — three cards
r1c1, r1c2, r1c3 = st.columns(3, gap="medium")
for col, (icon, title, desc), step_num in zip(
    [r1c1, r1c2, r1c3], steps[:3], ["Step 1", "Step 2", "Step 3"]
):
    with col:
        with st.container(border=True):
            st.markdown(
                f'<div class="cg-step-card">'
                f'<div class="cg-step-number">{step_num}</div>'
                f'<div class="cg-step-icon">{icon}</div>'
                f'<div class="cg-step-title">{title}</div>'
                f'<div class="cg-step-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

# Row 2 — two cards, centred
_, r2c1, r2c2, _ = st.columns([1, 2, 2, 1], gap="medium")
for col, (icon, title, desc), step_num in zip(
    [r2c1, r2c2], steps[3:], ["Step 4", "Step 5"]
):
    with col:
        with st.container(border=True):
            st.markdown(
                f'<div class="cg-step-card">'
                f'<div class="cg-step-number">{step_num}</div>'
                f'<div class="cg-step-icon">{icon}</div>'
                f'<div class="cg-step-title">{title}</div>'
                f'<div class="cg-step-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

st.divider()

# ─── Architecture & Call-to-Action ────────────────────────────────────────────
col_arch1, col_arch2 = st.columns([2, 1], gap="large")

with col_arch1:
    st.markdown("### Multi-Agent Pipeline")
    st.markdown(
        "CropGuardian AI runs a **sequential multi-agent pipeline** — "
        "either the **Google ADK Workflow** (Gemini-powered) or the "
        "**Legacy Coordinator** (deterministic Python). "
        "Both produce identical outputs, and the ADK engine falls back "
        "automatically if Gemini is unavailable."
    )
    st.markdown("")
    st.page_link("pages/1_Disease_Detection.py", label="Start Diagnosis →", icon="🔍")

with col_arch2:
    with st.container(border=True):
        st.markdown("**Pipeline Trace**")
        for i, agent in enumerate(
            ["DiseaseDetectionAgent", "WeatherAgent", "SeverityAgent",
             "EnvironmentalRiskAgent", "AdvisoryAgent"], 1
        ):
            st.markdown(
                f'<div class="cg-pipeline-step">'
                f'<div class="cg-pipeline-dot"></div>'
                f'<span><strong>{i}.</strong> <code>{agent}</code></span>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ─── Footer ───────────────────────────────────────────────────────────────────
render_footer()
