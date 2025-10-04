import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Selecciona un lugar en el mapa 🌍")

# Crear mapa centrado en Perú
m = folium.Map(location=[-9.19, -75.0152], zoom_start=5)

# Habilitar clics en el mapa
m.add_child(folium.LatLngPopup())

# Mostrar mapa en Streamlit
st_data = st_folium(m, width=700, height=500)

# Si el usuario hizo clic, mostramos las coordenadas
if st_data["last_clicked"] is not None:
    lat = st_data["last_clicked"]["lat"]
    lon = st_data["last_clicked"]["lng"]
    st.success(f"Coordenadas seleccionadas: Latitud = {lat:.6f}, Longitud = {lon:.6f}")