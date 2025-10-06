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
import json


from streamlit_folium import st_folium

full_df = vega_datasets.data("seattle_weather")

st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Eyes on the Sky ",
    page_icon="🌦️",
    # Make the content take up the width of the page:
    layout="wide",
)


"""
# Eyes on the Sky
## Is todate good for ....  hiking, picnic, biking, surfing, BBQ with friends?

You can see our source here: [dataset](https://disc.gsfc.nasa.gov/information/tools?title=Hydrology%20Time%20Series)!
### The app converts complex weather data into simple recommendations to help people choose where and when to go out.

## **Instructions**  
1. In the left panel, choose the variables you want to display for the prediction.  
2. Select the location and date/time of your planned activity.  
3. Click **Get forecast** to generate the weather summary.
Optinal: You can export in json :)
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
selected_set = set(selected_vars)

st.sidebar.markdown("### 📥 Export")
export_click = st.sidebar.button("Export JSON")


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
if "narrative" not in st.session_state:          # <--- NUEVO
    st.session_state.narrative = None            # <--- NUEVO
if "last_query" not in st.session_state:         # (opcional) para recordar la última consulta
    st.session_state.last_query = None


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
def render_kpi_rows(items, title):
    if not items:
        return
    st.markdown(f"### {title}")
    for i in range(0, len(items), 3):
        row  = items[i:i+3]
        cols = st.columns(3, gap="medium")
        for col, item in zip(cols, row):
            with col:
                st.metric(item["label"], item["value"])
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
                    st.session_state.last_query = {"lat": lat, "lon": lon, "date": str(date), "hour": hour}  # opcional

                    # Genera y GUARDA la descripción
                    with st.spinner("Generating weather summary..."):
                        narrative = describe_from_prediction(pred, activity=None)
                    st.session_state.narrative = narrative   # <--- CLAVE

                except requests.HTTPError as e:
                    st.session_state.api_error = e.response.text
                except Exception as e:
                    st.session_state.api_error = str(e)

            # Muestra error de API si lo hubo
            if st.session_state.api_error:
                st.error(f"API error: {st.session_state.api_error}")
    if st.session_state.narrative:                    
        st.markdown(st.session_state.narrative)       

prediction = st.session_state.prediction


if export_click:
    # Validación básica
    if lat is None or lon is None or date is None or hour is None:
        st.sidebar.warning("Selecciona ubicación en el mapa, fecha y hora antes de exportar.")
    else:
        try:
            pred = get_weather_prediction(lat, lon, date, hour)

            payload = {
                "query": {
                    "lat": float(lat),
                    "lon": float(lon),
                    "date": str(date),      # "YYYY-MM-DD"
                    "hour": int(hour),
                    "window_minutes": 60,   # ajusta si usas otro valor
                },
                "prediction": pred,
            }

            json_bytes = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
            fname = f"weather_{date}_{hour:02d}_{lat:.4f}_{lon:.4f}.json".replace(":", "")

            st.sidebar.download_button(
                label="⬇️ Download JSON",
                data=json_bytes,
                file_name=fname,
                mime="application/json",
            )

        except requests.HTTPError as e:
            st.sidebar.error(f"API error: {e.response.text}")
        except Exception as e:
            st.sidebar.error(f"Unexpected: {e}")




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
    kpis = [
    # Probabilities
    {"label": "Rain probability",        "value": f"{p_lluvia:.1f} %",   "group": "prob"},
    {"label": "Heat probability",        "value": f"{p_calor:.1f} %",    "group": "prob"},
    {"label": "Cold probability",        "value": f"{p_frio:.1f} %",     "group": "prob"},
    {"label": "Windy probability",       "value": f"{p_viento:.1f} %",   "group": "prob"},
    {"label": "Very humid probability",  "value": f"{p_muy_hum:.1f} %",  "group": "prob"},
    {"label": "Fog probability",         "value": f"{p_neblina:.2f} %",  "group": "prob"},

    # Aggregated stats
    {"label": "Mean temperature",        "value": f"{temp_c:.1f} °C",    "group": "stat"},
    {"label": "Mean wind",               "value": f"{viento_ms:.1f} m/s","group": "stat"},
    {"label": "Mean humidity",           "value": f"{hum_pct:.0f} %",    "group": "stat"},
    {"label": "Mean precipitation",      "value": f"{precip_mm_h:.3f} mm/h", "group": "stat"},
    ]
    kpis_selected = [k for k in kpis if k["label"] in selected_set]
    render_kpi_rows([k for k in kpis_selected if k["group"] == "prob"], "⛅ Probabilities")
    render_kpi_rows([k for k in kpis_selected if k["group"] == "stat"], "📊 Aggregated stats")
    note = prediction.get("note")

    st.write("")
    # ==== Probabilities chart (responde a selected_vars) ====
    probs_all = [
        {"label": "Rain probability",       "name": "Rain",       "value": p_lluvia},
        {"label": "Heat probability",       "name": "Heat",       "value": p_calor},
        {"label": "Cold probability",       "name": "Cold",       "value": p_frio},
        {"label": "Windy probability",      "name": "Windy",      "value": p_viento},
        {"label": "Very humid probability", "name": "Very humid", "value": p_muy_hum},
        {"label": "Fog probability",        "name": "Fog",        "value": p_neblina},
    ]

    # Filtrar según las variables elegidas
    probs_df = pd.DataFrame([p for p in probs_all if p["label"] in selected_set])

    # Solo mostrar si hay algo que graficar
    if not probs_df.empty:
        st.markdown("## 🌡️ Probabilities Overview")
        st.write("")   # espacio arriba

        bar = (
            alt.Chart(probs_df)
            .mark_bar(size=40)
            .encode(
                y=alt.Y("name:N", sort="-x", title=None),
                x=alt.X("value:Q", title="Probability (%)"),
                tooltip=[
                    "name",
                    alt.Tooltip("value:Q", format=".1f")
                ]
            )
            .properties(
                width=700,    # más ancho
                height=300,   # más alto
                title="Weather Event Probabilities"
            )
        )

        text = (
            alt.Chart(probs_df)
            .mark_text(align="left", dx=3, fontSize=14)
            .encode(
                y="name:N",
                x="value:Q",
                text=alt.Text("value:Q", format=".1f")
            )
        )

        st.altair_chart(bar + text, use_container_width=False)

        # espacio debajo
        st.markdown("<br><br>", unsafe_allow_html=True)

    if note:
        st.info(f"Note: {note}")
else:
    # Nada seleccionado todavía → no romper; UI limpia
    st.caption("Pick a location, date and hour, then click **Get forecast**.")

