# streamlit_app.py

import streamlit as st
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd  # Required for AQI aggregation

API_KEY = "8b8b77d1046f7ee6662731a0daa9483c"

AQI_CATEGORIES = [
    (50, "Good", "Air quality is satisfactory, and air pollution poses little or no risk."),
    (100, "Moderate", "Air quality is acceptable, but some pollutants may be a concern for sensitive groups."),
    (150, "Unhealthy for Sensitive Groups", "Children, elderly, and people with respiratory issues should limit outdoor activities."),
    (200, "Unhealthy", "Everyone may begin to experience adverse health effects; sensitive groups should stay indoors."),
    (300, "Very Unhealthy", "Health alert: everyone may experience more serious health effects."),
    (500, "Hazardous", "Emergency conditions. Entire population is more likely to be affected.")
]

POLLUTANT_PRECAUTIONS = {
    'pm2_5': """Wear an N95 mask outdoors.
Use HEPA air purifiers indoors.
Keep windows and doors closed.
Avoid outdoor exercise.
Monitor AQI apps frequently.
Seal gaps in windows to prevent air entry.
Keep plants indoors to absorb particulates.""",
    'pm10': """Limit time outdoors.
Keep house clean from dust.
Avoid construction zones.
Use wet mopping instead of sweeping.
Avoid outdoor burning.
Wear dust masks.
Ventilate only when air is clean.""",
    'no2': """Avoid high-traffic areas.
Do not burn firewood indoors.
Use electric stoves instead of gas.
Install air purifiers with activated carbon.
Ventilate kitchen and bathrooms properly.
Avoid smoking indoors.
Use public transport to reduce emissions.""",
    'so2': """Stay indoors during high levels.
Avoid burning coal or firewood.
Use cleaner cooking methods.
Ventilate your home well.
Install gas leak detectors.
Prefer electric heating.
Avoid industrial zones.""",
    'co': """Do not leave vehicles running in enclosed spaces.
Install CO detectors at home.
Ensure proper chimney ventilation.
Service gas appliances regularly.
Avoid smoking indoors.
Do not use charcoal grills indoors.
Keep room ventilated while using heaters.""",
    'o3': """Avoid exercise during midday.
Limit car usage.
Close windows on hot, sunny days.
Use indoor plants like aloe vera.
Stay indoors on ozone alert days.
Avoid gasoline-powered equipment.
Use public transit instead of driving."""
}

def convert_openweather_aqi(aqi_value):
    conversion_map = {1: 50, 2: 100, 3: 150, 4: 200, 5: 300}
    return conversion_map.get(aqi_value, 0)

def get_lat_lon(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    response = requests.get(url).json()
    if response:
        return response[0]['lat'], response[0]['lon']
    return None, None

def get_aqi_data(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    return requests.get(url).json()

def get_aqi_details(city):
    lat, lon = get_lat_lon(city)
    if not lat or not lon:
        st.error("City not found.")
        return
    data = get_aqi_data(lat, lon)
    if "list" not in data:
        st.error("AQI data unavailable.")
        return

    pollution_data = data['list'][0]
    aqi_openweather = pollution_data['main']['aqi']
    aqi = convert_openweather_aqi(aqi_openweather)

    for max_aqi, category, message in AQI_CATEGORIES:
        if aqi <= max_aqi:
            aqi_status = category
            aqi_message = message
            break

    pollutants = ['pm2_5', 'pm10', 'no2', 'so2', 'co', 'o3']
    values = [pollution_data['components'].get(p, 0) for p in pollutants]
    co_index = pollutants.index('co')
    co_ppb = pollution_data['components'].get('co', 0)
    values[co_index] = co_ppb * 0.001145

    max_pollutant = pollutants[values.index(max(values))]
    precaution = POLLUTANT_PRECAUTIONS.get(max_pollutant, "Follow general air quality precautions.")

    st.markdown(f"### AQI for {city}: {aqi} ({aqi_status})")
    st.markdown(f"""<div style="background-color:rgba(208, 235, 255, 0.35); padding:15px; border-left:6px solid #228be6; border-radius:6px;">
    <p style="font-weight:700; font-size:17px; color:#000000;">{aqi_message}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"### ⚠️ Main Pollutant: `{max_pollutant.upper()}`")
    st.markdown(f"""
    <div style="background-color:rgba(253, 243, 209, 0.35); padding:15px; border-radius:10px;">
    <p style="font-weight:900 !important; font-size:18px !important; color:#000000 !important; margin-bottom:10px;">⚠️ Precautions:</p>
    <ol style="font-weight:700; font-size:17px; color:#000000;">
    {''.join(f"<li>{line.strip()}</li>" for line in precaution.strip().splitlines())}
    </ol>
    </div>
    """, unsafe_allow_html=True)




    fig, ax = plt.subplots()
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown']
    bars = ax.bar(pollutants, values, color=colors)
    ax.set_title(f"Pollutant Levels in {city}")
    ax.set_xlabel("Pollutants")
    ax.set_ylabel("Concentration (µg/m³ or ppb)")
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f"{height:.1f}",
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    st.pyplot(fig)

# === Custom Page Settings ===
st.set_page_config(page_title="AIRAWARE - Air Quality Monitoring", layout="wide")

# === 🌆 BACKGROUND IMAGE SETTING ===
st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1950&q=80');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        filter: brightness(0.92);
    }
    .title-block {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        padding: 20px;
        color: #000000;  /* Pure black for visibility */
    }
    h1, h2, h3, h4, h5, h6, .markdown-text-container {
        font-weight: 800 !important;
    }
    .stMarkdown p {
        font-weight: 700 !important;
        font-size: 18px !important;
    }
    .stMetric label, .stMetric div {
        font-weight: 900 !important;
        font-size: 18px !important;
    }
    .element-container:has(.stMetric) {
        padding: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown("<div class='title-block'>🌫🌍️ AIRAWARE - Air Quality Monitoring System   🌫🌍</div>", unsafe_allow_html=True)

# === Sidebar navigation ===
if 'selected' not in st.session_state:
    st.session_state.selected = '📍 Check AQI of City'

col1, col2 = st.columns(2)
with col1:
    if st.button("📍 Check AQI of City", use_container_width=True):
        st.session_state.selected = '📍 Check AQI of City'
with col2:
    if st.button("🌤️ Today's Weather Report", use_container_width=True):
        st.session_state.selected = '🌤️ Today\'s Weather Report'
with col1:
    if st.button("📊 Air Quality Forecast", use_container_width=True):
        st.session_state.selected = '📊 Air Quality Forecast'
with col2:
    if st.button("📈 Historical AQI (Past 3 Days)", use_container_width=True):
        st.session_state.selected = '📈 Historical AQI (Past 3 Days)'

if st.session_state.selected == '📍 Check AQI of City':
    st.subheader("📍 Check AQI of City")
    city = st.text_input("### "**Enter your city name:**")
    if city:
        get_aqi_details(city)

elif st.session_state.selected == '🌤️ Today\'s Weather Report':
    st.subheader("🌤️ Today's Weather Report")
    city = st.text_input("Enter your city for weather:")
    if city:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") != 200:
            st.error(response.get("message", "City not found."))
        else:
            temp = response['main']['temp']
            humidity = response['main']['humidity']
            wind = response['wind']['speed']
            desc = response['weather'][0]['description'].title()
            icon = response['weather'][0]['icon']
            st.image(f"https://openweathermap.org/img/wn/{icon}@2x.png")
            st.metric("🌡️ Temperature", f"{temp} °C")
            st.metric("💧 Humidity", f"{humidity}%")
            st.metric("💨 Wind Speed", f"{wind} m/s")
            st.success(f"Condition: {desc}")

elif st.session_state.selected == '📊 Air Quality Forecast':
    st.subheader("📊 Air Quality Forecast - Next 3 Days")
    city = st.text_input("Enter your city for AQI Forecast:")
    if city:
        lat, lon = get_lat_lon(city)
        if lat and lon:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={API_KEY}"
            data = requests.get(url).json()
            forecast_data = data.get("list", [])
            if forecast_data:
                dates, aqis = [], []
                for i in range(0, min(len(forecast_data), 24 * 3), 8):
                    dt = datetime.fromtimestamp(forecast_data[i]['dt'])
                    dates.append(dt.strftime("%b %d %I%p"))
                    aqis.append(convert_openweather_aqi(forecast_data[i]['main']['aqi']))
                df = pd.DataFrame({"Date": dates, "AQI Forecast": aqis})
                df.set_index("Date", inplace=True)
                st.line_chart(df)
            else:
                st.warning("No forecast data available.")
        else:
            st.error("Unable to locate the city.")

elif st.session_state.selected == '📈 Historical AQI (Past 3 Days)':
    st.subheader("📈 Historical AQI - Past 3 Days")
    city = st.text_input("Enter your city for historical AQI:")
    if city:
        lat, lon = get_lat_lon(city)
        if lat and lon:
            now = int(datetime.utcnow().timestamp())
            past = int((datetime.utcnow() - timedelta(days=3)).timestamp())
            url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={past}&end={now}&appid={API_KEY}"
            data = requests.get(url).json()
            entries = data.get("list", [])
            if entries:
                df = pd.DataFrame([
                    {
                        "date": datetime.fromtimestamp(e["dt"]).strftime("%b %d"),
                        "aqi": convert_openweather_aqi(e["main"]["aqi"])
                    }
                    for e in entries
                ])
                daily_avg = df.groupby("date")["aqi"].mean().reset_index()
                daily_avg.set_index("date", inplace=True)
                st.line_chart(daily_avg.rename(columns={"aqi": "Past AQI"}))
            else:
                st.warning("No historical data available.")
        else:
            st.error("City not found.")
