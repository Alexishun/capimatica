from datetime import datetime, timedelta
import streamlit as st
import altair as alt
import pandas as pd
import vega_datasets
import folium
from folium.plugins import Fullscreen, MiniMap, MeasureControl, MousePosition
import altair as alt
import requests
from typing import Dict, Any, Tuple


from streamlit_folium import st_folium

full_df = vega_datasets.data("seattle_weather")

st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Capimatica ",
    page_icon="🌦️",
    # Make the content take up the width of the page:
    layout="wide",
)


"""
# Is todate good for ....  hiking, picnic, biking, surfing, BBQ with friends?

You can see our source here: [dataset](https://disc.gsfc.nasa.gov/information/tools?title=Hydrology%20Time%20Series)!
## The app converts complex weather data into simple recommendations to help people choose where and when to go out.
"""

""  # Add a little vertical space. Same as st.write("").
""

""
st.sidebar.header("⚙️ Options")
selected_vars = st.sidebar.multiselect(
    "Choose variables to display:",
    options=['Rain probability', 'Heat probability','Cold probability','Windy probability', 'Very humid probability', 'Fog probability', 'Mean temperature','Mean wind','Mean humidity','Mean precipitation'] ,
    default=['Rain probability', 'Mean temperature']
)
cols = st.columns(3)

URL = "https://capimatica.onrender.com/describe"

base = "http://capimatica.onrender.com"
BASE = "http://capimatica.onrender.com"
lat  = None
lon = None
date = None
empty_probs = None
empty_stats = None
empty_pred= None

hour= None

if "prediction" not in st.session_state:
    st.session_state.prediction = None
if "api_error" not in st.session_state:
    st.session_state.api_error = None

# Helpers robustos
def safe_get(d, key, default=None):
    try:
        return d.get(key, default) if isinstance(d, dict) else default
    except Exception:
        return default

def to_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def pct(x, nd=0, default=0.0):
    """Convierte prob en [0..1] a porcentaje y redondea."""
    try:
        return round(float(x) * 100.0, nd)
    except Exception:
        return default


def get_weather_prediction(lat, lon, date, hour, window_minutes=60):
    params = {
        "lat": lat, "lon": lon, "date": date,
        "hour": hour, "window_minutes": window_minutes
    }
    r = requests.get(f"{BASE}/weather", params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["prediction"] 

   


def describe_from_prediction(prediction: dict, activity: str | None = None) -> str:
    # prediction ya tiene keys: fecha_consulta, tabla, n_muestras, probs, stats...
    payload = {
        "fecha_consulta": prediction.get("fecha_consulta"),
        "tabla": prediction.get("tabla"),
        "n_muestras": prediction.get("n_muestras"),
        "prob_lluvia": prediction.get("prob_lluvia"),
        "prob_calor": prediction.get("prob_calor"),
        "prob_frio": prediction.get("prob_frio"),
        "prob_viento": prediction.get("prob_viento"),
        "prob_muy_humedo": prediction.get("prob_muy_humedo"),
        "prob_neblina": prediction.get("prob_neblina"),
        "note": prediction.get("note"),
        "stats": prediction.get("stats"),  # dict con temp_C_mean, etc.
        "activity": activity,              # opcional
    }
    r = requests.post(f"{BASE}/describe", json=payload, timeout=45)
    r.raise_for_status()
    return r.json().get("description", "")


# INPUT

col_map, col_right = st.columns([3, 2])

# INPUT MAPA

with col_map:
    st.markdown("### Where?")

    m = folium.Map(location=[-9.19, -75.0152], zoom_start=5, tiles="CartoDB positron")

    st_data = st_folium(m, width=800, height=350, key="main_map")

    if st_data and st_data.get("last_clicked"):
        lat = st_data["last_clicked"]["lat"]
        lon = st_data["last_clicked"]["lng"]
        st.success(f"Selected Location: Lat {lat:.4f}, Lon {lon:.4f}")
# Inputs de fecha y hora

with col_right:
    sub1, sub2 = st.columns([1, 1])
    with sub1:
        date = st.date_input("Date", value=datetime.utcnow().date())
    with sub2:
        hour = st.slider("Hour", 0, 23, value=16)

    st.markdown("### Weather Explainer")

    with st.container(border=True):
        if lat is None or lon is None:
            st.info("Click on the map to pick a location and select when.")
        elif date is None or hour is None:
            st.info("Choose a date and hour.")
        else:
            if st.button("Get forecast", use_container_width=True):
                try:
                    st.session_state.api_error = None
                    pred = get_weather_prediction(lat, lon, date, hour)
                    st.session_state.prediction = pred

                    # (Opcional) texto del LLM
                    with st.spinner("Generating weather summary..."):
                        narrative = describe_from_prediction(pred, activity=None)
                    st.markdown(narrative)

                except requests.HTTPError as e:
                    st.session_state.api_error = e.response.text
                except Exception as e:
                    st.session_state.api_error = str(e)

            # Muestra error de API si lo hubo
            if st.session_state.api_error:
                st.error(f"API error: {st.session_state.api_error}")

prediction = st.session_state.prediction
if prediction:
    # Helpers
    def safe_get(d, key, default=None):
        try:
            return d.get(key, default) if isinstance(d, dict) else default
        except Exception:
            return default

    def to_float(x, default=0.0):
        try: return float(x)
        except Exception: return default

    def pct(x, nd=0, default=0.0):
        try: return round(float(x) * 100.0, nd)
        except Exception: return default

    # Probabilidades (0..1 -> %)
    p_lluvia  = pct(safe_get(prediction, "prob_lluvia"),   nd=1)
    p_calor   = pct(safe_get(prediction, "prob_calor"),    nd=1)
    p_frio    = pct(safe_get(prediction, "prob_frio"),     nd=1)
    p_viento  = pct(safe_get(prediction, "prob_viento"),   nd=1)
    p_muy_hum = pct(safe_get(prediction, "prob_muy_humedo"), nd=1)
    p_neblina = pct(safe_get(prediction, "prob_neblina"),  nd=2)

    # Stats
    stats = safe_get(prediction, "stats", {}) or {}
    temp_c      = to_float(safe_get(stats, "temp_C_mean"),       default=0.0)
    precip_mm_h = to_float(safe_get(stats, "precip_mm_h_mean"),  default=0.0)
    viento_ms   = to_float(safe_get(stats, "viento_ms_mean"),    default=0.0)
    hum_raw     = to_float(safe_get(stats, "humedad_mean"),      default=0.0)
    hum_pct     = hum_raw * 100.0 if hum_raw <= 1 else hum_raw

    # Render dinámico según selected_vars (opcional: usa tu bloque dinámico)
    st.markdown("### ⛅ Probabilities")
    with st.container():
        cols = st.columns(3, gap="medium")
        with cols[0]: st.metric("Rain probability", p_lluvia)
        with cols[1]: st.metric("Heat probability", p_calor)
        with cols[2]: st.metric("Cold probability", p_frio)

        cols = st.columns(3, gap="medium")
        with cols[0]: st.metric("Windy probability", p_viento)
        with cols[1]: st.metric("Very humid probability", p_muy_hum)
        with cols[2]: st.metric("Fog probability", p_neblina)

    st.markdown("### 📊 Aggregated stats")
    with st.container():
        cols = st.columns(4, gap="medium")
        with cols[0]: st.metric("Mean temperature", f"{temp_c:.1f} °C")
        with cols[1]: st.metric("Mean wind", f"{viento_ms:.1f} m/s")
        with cols[2]: st.metric("Mean humidity", f"{hum_pct:.0f} %")
        with cols[3]: st.metric("Mean precipitation", f"{precip_mm_h:.3f} mm/h")

    note = prediction.get("note")
    if note:
        st.info(f"Note: {note}")
else:
    # Nada seleccionado todavía → no romper; UI limpia
    st.caption("Pick a location, date and hour, then click **Get forecast**.")