# styles.py — CropGuardian AI Shared Minimal Styles
import streamlit as st

def inject_css():
    """Injects CropGuardian AI global design system CSS."""
    st.markdown("""
    <style>
    /* ── Typography ───────────────────────────────────────────────────────── */
    .stApp,
    .stApp p, .stApp li, .stApp label,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stCaptionContainer"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter",
                     "Helvetica Neue", Arial, sans-serif;
    }

    /* ── Layout ───────────────────────────────────────────────────────────── */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 1280px;
    }

    /* ── Hero Section ─────────────────────────────────────────────────────── */
    .cg-hero-eyebrow {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--primary-color, #2E8B57);
        margin-bottom: 4px;
    }
    .cg-hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1.2;
        margin-bottom: 6px;
    }
    .cg-hero-subtitle {
        font-size: 1rem;
        font-weight: 500;
        opacity: 0.85;
        margin-bottom: 4px;
    }
    .cg-hero-desc {
        font-size: 0.88rem;
        opacity: 0.65;
        line-height: 1.55;
        max-width: 700px;
    }

    /* ── Section Labels ───────────────────────────────────────────────────── */
    .cg-section-label {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--primary-color, #2E8B57);
        margin-bottom: 8px;
        margin-top: 4px;
    }

    /* ── Disease Hero Card ────────────────────────────────────────────────── */
    .cg-disease-hero {
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.25;
        margin-bottom: 6px;
    }
    .cg-disease-healthy { color: var(--primary-color, #2E8B57); }

    /* ── Advisory List Items ──────────────────────────────────────────────── */
    .cg-adv-list { margin: 0; padding: 0; }
    .cg-adv-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 6px 0;
        border-bottom: 1px solid rgba(128,128,128,0.1);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .cg-adv-item:last-child { border-bottom: none; }
    .cg-adv-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: var(--primary-color, #2E8B57);
        margin-top: 7px;
        flex-shrink: 0;
    }

    /* ── Risk Reason Bar ──────────────────────────────────────────────────── */
    .cg-reason {
        font-size: 0.85rem;
        padding: 4px 0 4px 12px;
        border-left: 2px solid rgba(128,128,128,0.3);
        margin: 3px 0;
        line-height: 1.5;
    }

    /* ── Status Indicator ──────────────────────────────────────────────────── */
    .cg-status-cell {
        text-align: center;
        padding: 6px 0;
    }
    .cg-status-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        margin: 0 auto 5px auto;
    }
    .cg-status-dot.online  { background: #22c55e; }
    .cg-status-dot.offline { background: #ef4444; }
    .cg-status-dot.standby { background: #f59e0b; }
    .cg-status-label {
        font-size: 0.70rem;
        opacity: 0.60;
        margin-bottom: 2px;
    }
    .cg-status-value {
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* ── How-It-Works Step Cards ──────────────────────────────────────────── */
    .cg-step-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 8px 4px 6px 4px;
    }
    .cg-step-number {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--primary-color, #2E8B57);
        margin-bottom: 6px;
        opacity: 0.7;
    }
    .cg-step-icon {
        font-size: 1.8rem;
        margin-bottom: 8px;
        line-height: 1;
    }
    .cg-step-title {
        font-size: 0.92rem;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .cg-step-desc {
        font-size: 0.78rem;
        opacity: 0.65;
        line-height: 1.45;
    }

    /* ── Stat Cards ───────────────────────────────────────────────────────── */
    .cg-stat-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        justify-content: center;
        padding: 10px 8px;
    }
    .cg-stat-num {
        font-size: 2rem;
        font-weight: 800;
        color: var(--primary-color, #2E8B57);
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    .cg-stat-lbl {
        font-size: 0.78rem;
        font-weight: 500;
        margin-top: 4px;
        opacity: 0.7;
    }

    /* ── Bordered container global hover ──────────────────────────────────── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 10px !important;
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 3px 12px rgba(46,139,87,0.08) !important;
        border-color: var(--primary-color, #2E8B57) !important;
    }

    /* ── Metric value/label — prevent truncation ─────────────────────────── */
    [data-testid="stMetricValue"] {
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }

    /* ── Pipeline trace list ──────────────────────────────────────────────── */
    .cg-pipeline-step {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 0;
        font-size: 0.82rem;
        border-bottom: 1px solid rgba(128,128,128,0.06);
    }
    .cg-pipeline-step:last-child { border-bottom: none; }
    .cg-pipeline-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: var(--primary-color, #2E8B57);
        flex-shrink: 0;
    }

    /* ── CTA Button ──────────────────────────────────────────────────────── */
    .cg-cta-area {
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
