# weather_card.py — CropGuardian AI Meteorological Renderer
import streamlit as st

def get_risk_colored_string(level: str) -> str:
    """Helper returning a standard color markdown string based on risk level."""
    l = level.lower()
    if "very high" in l or "high" in l:
        return f":red[{level}]"
    elif "medium" in l or "moderate" in l:
        return f":orange[{level}]"
    elif "low" in l or "healthy" in l:
        return f":green[{level}]"
    else:
        return f":grey[{level}]"

def render_weather_card(weather_data: dict, risk_data: dict = None):
    """Renders location-aware weather conditions and environmental risk assessments."""
    st.markdown("<div class='cg-section-label'>Environmental Intelligence</div>", unsafe_allow_html=True)
    
    if weather_data and "error" not in weather_data:
        w = weather_data.get("weather", {})
        st.caption(f"📍 Location Context: **{weather_data.get('location', 'Unknown')}**")
        
        # Grid layout for metrics
        wc1, wc2, wc3, wc4 = st.columns(4)
        with wc1:
            st.metric("🌡 Temperature", f"{w.get('temperature','—')}°C", delta=f"Feels like {w.get('feels_like','—')}°C", delta_color="off")
        with wc2:
            st.metric("💧 Humidity", f"{w.get('humidity','—')}%")
        with wc3:
            st.metric("🌧 Precipitation", f"{w.get('precipitation','—')} mm")
        with wc4:
            st.metric("💨 Wind Speed", f"{w.get('wind_speed','—')} km/h")
            
        if w.get("cloud_cover") is not None:
            st.caption(
                f"Cloud cover: {w.get('cloud_cover')}%  ·  "
                f"Gusts: {w.get('wind_gusts','—')} km/h  ·  "
                f"Pressure: {w.get('pressure','—')} hPa"
            )
    else:
        st.info("🌦 Weather data unavailable. Provide a farm location during analysis to enable environmental metrics.")

    # Risk Breakdown
    if risk_data and "error" not in risk_data:
        st.markdown("<div class='cg-section-label' style='margin-top:16px;'>Disease Risk Factors</div>", unsafe_allow_html=True)
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            with st.container(border=True):
                st.markdown(f"🍄 **Fungal Risk**")
                st.markdown(f"Level: {get_risk_colored_string(risk_data.get('fungal_risk', 'Unknown'))}")
        with rc2:
            with st.container(border=True):
                st.markdown(f"🦠 **Bacterial Risk**")
                st.markdown(f"Level: {get_risk_colored_string(risk_data.get('bacterial_risk', 'Unknown'))}")
        with rc3:
            with st.container(border=True):
                st.markdown(f"🌡️ **Heat Stress**")
                st.markdown(f"Level: {get_risk_colored_string(risk_data.get('heat_stress_risk', 'Unknown'))}")
                
        # Risk reasons
        reasons = risk_data.get("reasons", [])
        if reasons:
            st.markdown("")
            for reason in reasons:
                st.markdown(f"<div class='cg-reason'>• {reason}</div>", unsafe_allow_html=True)

def render_weather_snapshot(weather_data: dict):
    """Renders a compact, farmer-friendly weather snapshot."""
    if not weather_data or "error" in weather_data or weather_data.get("status") in ["failed", "unavailable", "timeout"]:
        return

    w = weather_data.get("weather", {})
    location = weather_data.get("location", "Unknown Location")
    
    temp = w.get("temperature", "—")
    humidity = w.get("humidity", "—")
    # Use cloud cover as a proxy for rain probability
    rain_prob = w.get("cloud_cover", 0)
    if rain_prob is None:
        rain_prob = 0
    
    # Format location cleanly (take first part for the card size)
    parts = [p.strip() for p in location.split(",")]
    clean_location = parts[0] if parts else location

    # Inject lightweight hover, shadow, and rounded corner styling for the cards
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03) !important;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out, border-color 0.2s ease-in-out !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08) !important;
            border-color: var(--primary-color, #2E8B57) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.subheader("🌦️ Current Weather Conditions")
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.metric(label="🌡️ Temp", value=f"{temp}°C")
            
    with col2:
        with st.container(border=True):
            st.metric(label="💧 Humidity", value=f"{humidity}%")
            
    with col3:
        with st.container(border=True):
            st.metric(label="🌧️ Rain", value=f"{rain_prob}%")
            
    with col4:
        with st.container(border=True):
            st.metric(label="📍 Location", value=clean_location)

    st.info("Current weather conditions may influence disease spread.")
