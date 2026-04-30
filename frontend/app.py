import streamlit as st
import requests

st.set_page_config(page_title="Agri Price AI", layout="wide")

API_URL = "http://127.0.0.1:8000/predict"
WEATHER_URL = "http://127.0.0.1:8000/weather"

# --- Initialize Session State ---
# This ensures we have "starting" values so the model doesn't crash
if 'live_temp' not in st.session_state:
    st.session_state.live_temp = 30.0
    st.session_state.live_humidity = 50.0
    st.session_state.live_rain = 0.0

st.title("🚜 Agri Price AI: Smart Mandi Forecasting")

# --- SIDEBAR: Weather ---
st.sidebar.header("📍 Mandi Location")
city = st.sidebar.text_input("Enter City", "Nagpur")

if st.sidebar.button("Update Weather"):
    try:
        w_resp = requests.get(f"{WEATHER_URL}/{city}")
        if w_resp.status_code == 200:
            data = w_resp.json()
            # SAVE the real data to session state
            st.session_state.live_temp = float(data['temp'])
            st.session_state.live_humidity = float(data['humidity'])
            st.session_state.live_rain = float(data.get('rain', 0.0))
            
            st.sidebar.success(f"Updated! Temp: {st.session_state.live_temp}°C")
        else:
            st.sidebar.error("City not found, using default weather.")
    except:
        st.sidebar.error("Weather API Offline")

# --- SIDEBAR: Price Inputs ---
st.sidebar.markdown("---")
st.sidebar.header("Price Parameters")
month = st.sidebar.slider("Month", 1, 12, 5)
yesterday_price = st.sidebar.number_input("Yesterday's Price", value=2100.0)
seven_day_avg = st.sidebar.number_input("7-Day Avg Price", value=2050.0)

# --- MAIN PAGE: Prediction ---
# Build payload using the LIVE weather data from session state
payload = {
    "month": int(month),
    "yesterday_price": float(yesterday_price),
    "seven_day_avg": float(seven_day_avg),
    "temp": st.session_state.live_temp,
    "humidity": st.session_state.live_humidity,
    "rainfall": st.session_state.live_rain
}

if st.button("Predict Future Price", key="predict_final"):
    try:
        with st.spinner(f"Analyzing trends for {city}..."):
            response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if "prediction" in result:
                st.balloons()
                st.success(f"### 📈 Predicted Price: ₹{result['prediction']}")
                st.info(f"💡 This prediction accounts for {city}'s current temperature of {st.session_state.live_temp}°C.")
            else:
                st.error(f"AI Error: {result.get('error')}")
    except:
        st.error("Connection to Engine failed.")