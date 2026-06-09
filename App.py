import requests
import streamlit as st
import folium
import plotly.graph_objects as go
from datetime import datetime
from streamlit_folium import st_folium

if "trail" not in st.session_state:
    st.session_state.trail = []

st.set_page_config(page_title="ISS Mission Control", layout="wide")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0b1f33 0%, #050b16 55%, #02040a 100%);
    color: #e6fbff;
}

.block-container {
    padding-top: 0.7rem;
    padding-left: 0.8rem;
    padding-right: 0.8rem;
    max-width: 100%;
}

h1, h2, h3 {
    color: #9ffcff !important;
    text-shadow: 0 0 12px #00eaff;
}

[data-testid="stMetric"] {
    background: rgba(5, 25, 45, 0.92);
    border: 1px solid #00eaff;
    border-radius: 12px;
    padding: 8px;
    box-shadow: 0 0 10px rgba(0,234,255,0.35);
    min-height: 78px;
}

[data-testid="stMetricValue"] div {
    font-size: 26px !important;
}

[data-testid="stMetricLabel"] div {
    font-size: 13px !important;
}

[data-testid="stMetricLabel"] {
    color: #7df9ff !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    text-shadow: 0 0 8px #00eaff;
    font-weight: 800;
}

iframe {
    border: 1px solid #00eaff;
    border-radius: 16px;
    box-shadow: 0 0 20px rgba(0,234,255,0.35);
}
</style>
""", unsafe_allow_html=True)

st.title("🛰️ International Space Station: Live Tracker")

top1, top2 = st.columns([3, 1])

with top1:
    st.caption("UTC Time: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

with top2:
    if st.button("🔄 Refresh ISS Position"):
        st.rerun()

url = "https://api.wheretheiss.at/v1/satellites/25544"
response = requests.get(url)
data = response.json()

crew_url = "http://api.open-notify.org/astros.json"
crew_response = requests.get(crew_url)
crew_data = crew_response.json()

latitude = data["latitude"]
longitude = data["longitude"]
altitude = data["altitude"]
velocity = data["velocity"]
viewer_lat = st.sidebar.number_input("Viewer latitude", value=51.5072)
viewer_lon = st.sidebar.number_input("Viewer longitude", value=-0.1276)

pass_url = f"http://api.open-notify.org/iss-pass.json?lat={viewer_lat}&lon={viewer_lon}&n=1"

try:
    pass_response = requests.get(pass_url)
    pass_data = pass_response.json()

    next_pass = pass_data["response"][0]
    rise_time = next_pass["risetime"]
    duration = next_pass["duration"]

    next_pass_text = datetime.utcfromtimestamp(rise_time).strftime("%d %b, %H:%M UTC")
    next_pass_duration = str(round(duration / 60, 1)) + " min"

except:
    next_pass_text = "Unavailable"
    next_pass_duration = "Unknown"

place_name = "Live ISS Position"
region = "Earth Orbit"
country_code = "ISS"

st.session_state.trail.append([latitude, longitude])

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Latitude", round(latitude, 2))
col2.metric("Longitude", round(longitude, 2))
col3.metric("Altitude", str(round(altitude, 2)) + " km")
col4.metric("Velocity", str(round(velocity, 2)) + " km/h")
col5.metric("People in Space", crew_data["number"])

status1, status2, status3, status4, status5 = st.columns(5)

with status1:
    st.metric("🚀 Orbit", "Active")

with status2:
    st.metric("🌍 Location", place_name)

with status3:
    st.metric("📍 Region", region)

with status4:
    st.metric("🛰️ Next Pass", next_pass_text)

with status5:
    st.metric("⏱️ Duration", next_pass_duration)

fig = go.Figure()

fig.add_trace(go.Scattergeo(
    lon=[point[1] for point in st.session_state.trail],
    lat=[point[0] for point in st.session_state.trail],
    mode="lines",
    line=dict(width=8, color="rgba(0, 234, 255, 0.25)"),
    name="ISS Trail Glow"
))

fig.add_trace(go.Scattergeo(
    lon=[point[1] for point in st.session_state.trail],
    lat=[point[0] for point in st.session_state.trail],
    mode="lines",
    line=dict(width=3, color="#FFFFFF"),
    name="ISS Trail"
))

fig.add_trace(go.Scattergeo(
    lon=[longitude],
    lat=[latitude],
    mode="markers+text",
    marker=dict(
        size=24,
        color="#00EAFF",
        line=dict(width=3, color="#FFFFFF")
    ),
    text=["ISS"],
    textfont=dict(size=16, color="#FFFFFF"),
    textposition="top center",
    name="ISS"
))

fig.update_geos(
    projection_type="orthographic",
    projection_rotation=dict(lon=longitude, lat=latitude),
    showland=True,
    landcolor="rgb(30, 90, 90)",
    showocean=True,
    oceancolor="rgb(5, 20, 55)",
    showcountries=True,
    countrycolor="rgb(0, 234, 255)",
    showcoastlines=True,
    coastlinecolor="rgb(0, 234, 255)",
    bgcolor="rgba(0,0,0,0)"
)

fig.update_layout(
    height=500,
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

m = folium.Map(
    location=[latitude, longitude],
    zoom_start=4,
    tiles="CartoDB dark_matter"
)

folium.PolyLine(
    st.session_state.trail,
    color="#00EAFF",
    weight=8,
    opacity=0.25
).add_to(m)

folium.PolyLine(
    st.session_state.trail,
    color="#FFFFFF",
    weight=3
).add_to(m)

iss_icon = folium.DivIcon(
    html="""
    <div style="
        font-size:30px;
        color:white;
        text-shadow:
        0 0 8px #00EAFF,
        0 0 16px #00EAFF,
        0 0 24px #00EAFF;
    ">🛰️</div>
    """
)

folium.Marker(
    [latitude, longitude],
    popup="ISS",
    tooltip="International Space Station",
    icon=iss_icon
).add_to(m)

left, right = st.columns(2)

with left:
    st.markdown("### 🌍 3D Earth View")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### 🗺️ ISS Tracking Map")
    st_folium(m, width=650, height=500)

with st.expander("👩‍🚀 People Currently in Space"):
    cols = st.columns(4)

    for i, person in enumerate(crew_data["people"]):
        with cols[i % 4]:
            st.caption(person["name"])
