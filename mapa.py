from datetime import datetime, timedelta
import streamlit as st
import altair as alt
import pandas as pd
import vega_datasets
import folium
from folium.plugins import Fullscreen, MiniMap, MeasureControl, MousePosition
import altair as alt

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
# Is today good for ....  hiking, picnic, biking, surfing, BBQ with friends?

Let's explore in [dataset](https://disc.gsfc.nasa.gov/information/tools?title=Hydrology%20Time%20Series)!
## The app converts complex weather data into simple recommendations to help people choose where and when to go out.
"""

""  # Add a little vertical space. Same as st.write("").
""

""


def weather_explainer(temp_c, feels_c, humidity, wind_ms, rain_prob, uv):
    return "El clima estará de la csmre de su reputaperra madre por la re mil puta que te pario"
col_map, col_right = st.columns([3, 2])



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
        day = st.date_input("Date", value=datetime.utcnow().date())
    with sub2:
        hour = st.slider("Hour", 0, 23, value=16)

    st.markdown("### Weather Explainer")

    with st.container(border=True):
        # (Ejemplo con datos ficticios; cámbialos por los reales)
        temp_c      = 24.2
        feels_c     = 25.0
        humidity    = 58
        wind_ms     = 3.6
        rain_prob   = 22
        uv_index    = 6.5

        # Lógica simple para texto descriptivo
        narrative = weather_explainer(
            temp_c=temp_c,
            feels_c=feels_c,
            humidity=humidity,
            wind_ms=wind_ms,
            rain_prob=rain_prob,
            uv=uv_index
        )

        st.markdown(narrative)

# Data de ejemplo
weather_data = {
    "Temperature (°C)": 26.4,
    "Feels like (°C)": 27.0,
    "Humidity (%)": 58,
    "Wind speed (m/s)": 3.2,
    "Rain probability (%)": 35,
    "UV Index": 6.8,
}

df = pd.DataFrame(list(weather_data.items()), columns=["Variable", "Value"])

st.sidebar.header("⚙️ Options")
selected_vars = st.sidebar.multiselect(
    "Choose variables to display:",
    options=['temp', 'sensación','humedad','viento', 'prob. de lluvia', 'UV'] ,
    default=['temp', 'sensación','humedad','viento', 'prob. de lluvia', 'UV']
)
cols = st.columns(3)



filtered_df = df[df["Variable"].isin(selected_vars)]

for i, (var, val) in enumerate(zip(filtered_df["Variable"], filtered_df["Value"])):
    with cols[i % 3]:
        st.metric(label=var, value=f"{val}")
st.subheader("📊 Graph of selected variables")
if not filtered_df.empty:
    chart = (
        alt.Chart(filtered_df)
        .mark_bar(color="#4c9aff")
        .encode(
            x=alt.X("Variable", sort=None, title="Weather Variables"),
            y=alt.Y("Value", title="Value"),
            tooltip=["Variable", "Value"]
        )
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Please select at least one variable to display the graph.")

# ---------------------------
# Exportar a JSON
# ---------------------------
st.subheader("📥 Export data")
if st.button("Export as JSON"):
    json_str = json.dumps(filtered_df.set_index("Variable")["Value"].to_dict(), indent=4)
    st.download_button(
        label="⬇Download JSON",
        data=json_str,
        file_name="weather_data.json",
        mime="application/json"
    )




df_2015 = full_df[full_df["date"].dt.year == 2015]
df_2014 = full_df[full_df["date"].dt.year == 2014]

max_temp_2015 = df_2015["temp_max"].max()
max_temp_2014 = df_2014["temp_max"].max()

min_temp_2015 = df_2015["temp_min"].min()
min_temp_2014 = df_2014["temp_min"].min()

max_wind_2015 = df_2015["wind"].max()
max_wind_2014 = df_2014["wind"].max()

min_wind_2015 = df_2015["wind"].min()
min_wind_2014 = df_2014["wind"].min()

max_prec_2015 = df_2015["precipitation"].max()
max_prec_2014 = df_2014["precipitation"].max()

min_prec_2015 = df_2015["precipitation"].min()
min_prec_2014 = df_2014["precipitation"].min()



weather_data = {
    "Temperature (°C)": 26.4,
    "Feels like (°C)": 27.0,
    "Humidity (%)": 58,
    "Wind speed (m/s)": 3.2,
    "Rain probability (%)": 35,
    "UV Index": 6.8,
}
with st.container(horizontal=True, gap="medium"):
    cols = st.columns(2, gap="medium", width=300)

    with cols[0]:
        st.metric(
            "Max tempearture",
            f"{max_temp_2015:0.1f}C",
            delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
            width="content",
        )

    with cols[1]:
        st.metric(
            "Min tempearture",
            f"{min_temp_2015:0.1f}C",
            delta=f"{min_temp_2015 - min_temp_2014:0.1f}C",
            width="content",
        )

    cols = st.columns(2, gap="medium", width=300)

    with cols[0]:
        st.metric(
            "Max precipitation",
            f"{max_prec_2015:0.1f}C",
            delta=f"{max_prec_2015 - max_prec_2014:0.1f}C",
            width="content",
        )

    with cols[1]:
        st.metric(
            "Min precipitation",
            f"{min_prec_2015:0.1f}C",
            delta=f"{min_prec_2015 - min_prec_2014:0.1f}C",
            width="content",
        )

    cols = st.columns(2, gap="medium", width=300)

    with cols[0]:
        st.metric(
            "Max wind",
            f"{max_wind_2015:0.1f}m/s",
            delta=f"{max_wind_2015 - max_wind_2014:0.1f}m/s",
            width="content",
        )

    with cols[1]:
        st.metric(
            "Min wind",
            f"{min_wind_2015:0.1f}m/s",
            delta=f"{min_wind_2015 - min_wind_2014:0.1f}m/s",
            width="content",
        )

    cols = st.columns(2, gap="medium", width=300)

    weather_icons = {
        "sun": "☀️",
        "snow": "☃️",
        "rain": "💧",
        "fog": "😶‍🌫️",
        "drizzle": "🌧️",
    }

    with cols[0]:
        weather_name = (
            full_df["weather"].value_counts().head(1).reset_index()["weather"][0]
        )
        st.metric(
            "Most common weather",
            f"{weather_icons[weather_name]} {weather_name.upper()}",
        )

    with cols[1]:
        weather_name = (
            full_df["weather"].value_counts().tail(1).reset_index()["weather"][0]
        )
        st.metric(
            "Least common weather",
            f"{weather_icons[weather_name]} {weather_name.upper()}",
        )

""
""




# """
# ## Compare different years
# """

# YEARS = full_df["date"].dt.year.unique()
# selected_years = st.pills(
#     "Years to compare", YEARS, default=YEARS, selection_mode="multi"
# )

# if not selected_years:
#     st.warning("You must select at least 1 year.", icon=":material/warning:")

# df = full_df[full_df["date"].dt.year.isin(selected_years)]

# cols = st.columns([3, 1])

# with cols[0].container(border=True, height="stretch"):
#     "### Temperature"

#     st.altair_chart(
#         alt.Chart(df)
#         .mark_bar(width=1)
#         .encode(
#             alt.X("date", timeUnit="monthdate").title("date"),
#             alt.Y("temp_max").title("temperature range (C)"),
#             alt.Y2("temp_min"),
#             alt.Color("date:N", timeUnit="year").title("year"),
#             alt.XOffset("date:N", timeUnit="year"),
#         )
#         .configure_legend(orient="bottom")
#     )

# with cols[1].container(border=True, height="stretch"):
#     "### Weather distribution"

#     st.altair_chart(
#         alt.Chart(df)
#         .mark_arc()
#         .encode(
#             alt.Theta("count()"),
#             alt.Color("weather:N"),
#         )
#         .configure_legend(orient="bottom")
#     )


# cols = st.columns(2)

# with cols[0].container(border=True, height="stretch"):
#     "### Wind"

#     st.altair_chart(
#         alt.Chart(df)
#         .transform_window(
#             avg_wind="mean(wind)",
#             std_wind="stdev(wind)",
#             frame=[0, 14],
#             groupby=["monthdate(date)"],
#         )
#         .mark_line(size=1)
#         .encode(
#             alt.X("date", timeUnit="monthdate").title("date"),
#             alt.Y("avg_wind:Q").title("average wind past 2 weeks (m/s)"),
#             alt.Color("date:N", timeUnit="year").title("year"),
#         )
#         .configure_legend(orient="bottom")
#     )

# with cols[1].container(border=True, height="stretch"):
#     "### Precipitation"

#     st.altair_chart(
#         alt.Chart(df)
#         .mark_bar()
#         .encode(
#             alt.X("date:N", timeUnit="month").title("date"),
#             alt.Y("precipitation:Q").aggregate("sum").title("precipitation (mm)"),
#             alt.Color("date:N", timeUnit="year").title("year"),
#         )
#         .configure_legend(orient="bottom")
#     )

# cols = st.columns(2)

# with cols[0].container(border=True, height="stretch"):
#     "### Monthly weather breakdown"
#     ""

#     st.altair_chart(
#         alt.Chart(df)
#         .mark_bar()
#         .encode(
#             alt.X("month(date):O", title="month"),
#             alt.Y("count():Q", title="days").stack("normalize"),
#             alt.Color("weather:N"),
#         )
#         .configure_legend(orient="bottom")
#     )

# with cols[1].container(border=True, height="stretch"):
#     "### Raw data"

#     st.dataframe(df)