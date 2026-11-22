# header.py — CropGuardian AI Hero Header & Telemetry Panels
import os
import sys
import streamlit as st
from ui.status_panel import check_gemini_api_cached, check_weather_api_cached
from config.constants import APP_VERSION, MODEL_VERSION

@st.cache_data(ttl=3600)
def get_dataset_size() -> int:
    """Calculates the total number of images stored recursively under data/."""
    count = 0
    data_dir = "data"
    if os.path.exists(data_dir):
        for _, _, files in os.walk(data_dir):
            count += len(files)
    return count

@st.cache_resource
def _get_static_telemetry() -> dict:
    """Caches static platform info that never changes during a server's lifetime.
    Uses @st.cache_resource so it runs exactly once per Streamlit server process."""
    import platform
    import tensorflow as tf
    return {
        "os": platform.platform(),
        "arch": f"{platform.machine()} ({platform.architecture()[0]})",
        "processor": platform.processor(),
        "python": sys.version.split()[0],
        "tf_version": tf.__version__,
        "gpus": tf.config.list_physical_devices('GPU'),
    }

def render_header(title: str = "CropGuardian AI", subtitle: str = "AI-Powered Crop Disease Detection & Farmer Advisory System", show_metrics: bool = False):
    """Renders the main layout headers, dynamic status cards, and the system telemetry panel."""

    # ── Hero — clean text hierarchy, no custom HTML widgets ──────────────
    st.markdown(
        '<div class="cg-hero-eyebrow">AI-Powered Agricultural Intelligence</div>'
        f'<div class="cg-hero-title">{title}</div>'
        f'<div class="cg-hero-subtitle">{subtitle}</div>'
        '<div class="cg-hero-desc">'
        'Detect crop diseases from leaf images, assess weather-driven spread risk, '
        'and receive personalised treatment plans — powered by MobileNetV2 &amp; Gemini.'
        '</div>',
        unsafe_allow_html=True,
    )

    if show_metrics:
        # ── Service Status — compact inline indicators ───────────────────
        model_loaded  = "pipeline_response" in st.session_state or st.session_state.get("model_loaded", False)
        gemini_ok     = check_gemini_api_cached()
        weather_ok    = check_weather_api_cached()
        workflow_mode = st.session_state.get("workflow_mode", "Google ADK Workflow")
        dataset_size  = get_dataset_size()
        orch_label    = "ADK Workflow" if "ADK" in workflow_mode else "Legacy Engine"

        st.markdown("")  # tiny spacer

        with st.container(border=True):
            s1, s2, s3, s4, s5 = st.columns(5)
            with s1:
                _status_dot("Model", "Ready" if model_loaded else "Standby", "online" if model_loaded else "standby")
            with s2:
                _status_dot("Weather API", "Online" if weather_ok else "Offline", "online" if weather_ok else "offline")
            with s3:
                _status_dot("Gemini API", "Active" if gemini_ok else "Offline", "online" if gemini_ok else "offline")
            with s4:
                _status_dot("Orchestrator", orch_label, "online")
            with s5:
                _status_dot("Dataset", f"{dataset_size:,} images", "online")

        # ── System Health — tucked away for developers ───────────────────
        with st.expander("🖥️ System Health Telemetry"):
            st.caption("Diagnostic information for administrators and developers.")
            static = _get_static_telemetry()

            col_sys1, col_sys2 = st.columns(2)
            with col_sys1:
                st.markdown("**Machine Platform**")
                st.write(f"- **OS**: `{static['os']}`")
                st.write(f"- **Architecture**: `{static['arch']}`")
                st.write(f"- **Processor**: `{static['processor']}`")
                import psutil
                ram = psutil.virtual_memory()
                st.write(f"- **RAM**: `{ram.available / (1024**3):.1f} GB / {ram.total / (1024**3):.1f} GB` ({ram.percent}% used)")
            with col_sys2:
                st.markdown("**Engine & Model**")
                st.write(f"- **Python**: `{static['python']}`")
                st.write(f"- **TensorFlow**: `{static['tf_version']}`")
                st.write(f"- **GPU**: `{static['gpus'] if static['gpus'] else 'None (CPU)'}`")
                st.write(f"- **Model**: `{MODEL_VERSION}`")
                st.write(f"- **App**: `{APP_VERSION}`")


def _status_dot(label: str, value: str, state: str = "online"):
    """Renders a single compact status indicator with a coloured dot."""
    st.markdown(
        f'<div class="cg-status-cell">'
        f'<div class="cg-status-dot {state}"></div>'
        f'<div class="cg-status-label">{label}</div>'
        f'<div class="cg-status-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
