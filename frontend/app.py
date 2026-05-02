import streamlit as st
import requests
import joblib
import os
import pandas as pd
import numpy as np

# --- 1. Page Configuration ---
st.set_page_config(page_title="Agri Price AI", layout="wide")

# --- 2. Load Model (Prevents NameError) ---
# This looks for the model in your 'models' folder
MODEL_PATH = os.path.join("models", "best_model.pkl")
model = None

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        st.error(f"Error loading model: {e}")
else:
    # We define it as None so the 'if model:' check later doesn't crash the app
    model = None

# --- 3. URL Configuration ---
# Used for the first 'Predict' button logic
API_URL = "http://127.0.0.1:8000/predict"
WEATHER_URL = "http://127.0.0.1:8000/weather"

# --- 4. Initialize Session State ---
if 'live_temp' not in st.session_state:
    st.session_state.live_temp = 30.0
    st.session_state.live_humidity = 50.0
    st.session_state.live_rain = 0.0

st.title("🚜 Agri Price AI: Smart Mandi Forecasting")

# --- 5. SIDEBAR: Weather & Inputs ---
st.sidebar.header("📍 Mandi Location")
city = st.sidebar.text_input("Enter City", "Nagpur")

if st.sidebar.button("Update Weather"):
    try:
        w_resp = requests.get(f"{WEATHER_URL}/{city}")
        if w_resp.status_code == 200:
            data = w_resp.json()
            st.session_state.live_temp = float(data['temp'])
            st.session_state.live_humidity = float(data['humidity'])
            st.session_state.live_rain = float(data.get('rain', 0.0))
            st.sidebar.success(f"Updated! Temp: {st.session_state.live_temp}°C")
        else:
            st.sidebar.error("City not found, using default weather.")
    except:
        st.sidebar.error("Weather API Offline - Using Default")

st.sidebar.markdown("---")
st.sidebar.header("Price Parameters")
month = st.sidebar.slider("Month", 1, 12, 5)
yesterday_price = st.sidebar.number_input("Yesterday's Price", value=2100.0)
seven_day_avg = st.sidebar.number_input("7-Day Avg Price", value=2050.0)

# --- 6. MAIN PAGE: Analysis & Charts ---

# Common Payload for both logic paths
payload = {
    "month": int(month),
    "yesterday_price": float(yesterday_price),
    "seven_day_avg": float(seven_day_avg),
    "temp": st.session_state.live_temp,
    "humidity": st.session_state.live_humidity,
    "rainfall": st.session_state.live_rain
}

# --- BUTTON 1: API PREDICTION ---
if st.button("Predict via API Engine", key="predict_api"):
    try:
        with st.spinner(f"Contacting API for {city}..."):
            response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if "prediction" in result:
                st.balloons()
                st.success(f"### 📈 API Predicted Price: ₹{result['prediction']}")
            else:
                st.error(f"AI Error: {result.get('error')}")
    except:
        st.error("Connection to FastAPI Engine failed. Try the 'Direct Calculate' button below.")

st.write("---")

# --- BUTTON 2: LOCAL CALCULATION WITH CHARTS ---
if st.button("Calculate via Local Model (with Charts)"):
    if model is not None:
        with st.spinner("Processing local model inference..."):
            # 1. Prediction Logic
            input_df = pd.DataFrame([[
                month, yesterday_price, seven_day_avg, 
                st.session_state.live_temp, st.session_state.live_humidity, st.session_state.live_rain
            ]], columns=['month', 'yesterday_price', 'seven_day_avg', 'temp', 'humidity', 'rainfall'])
            
            prediction = model.predict(input_df)[0]
            
            # 2. Display Results Metrics
            st.balloons()
            st.subheader("📊 Market Analysis Results")
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.metric(label="Tomorrow's Forecast", value=f"₹{round(prediction, 2)}", 
                          delta=f"{round(prediction - yesterday_price, 2)} from yesterday")
            
            with col_res2:
                st.metric(label="7-Day Average", value=f"₹{seven_day_avg}")

            # 3. Price Trend Visualization
            st.write("---")
            st.subheader("📈 Price Trend Visualization")
            
            chart_data = pd.DataFrame({
                'Timeframe': ['7-Day Avg', 'Yesterday', 'Predicted'],
                'Price (₹)': [seven_day_avg, yesterday_price, prediction]
            }).set_index('Timeframe')

            st.line_chart(chart_data, use_container_width=True)
            
            # 4. Prediction Confidence View
            st.write("### Prediction Confidence View")
            confidence_data = pd.DataFrame({
                "Min Price": [prediction * 0.98],
                "Predicted": [prediction],
                "Max Price": [prediction * 1.02]
            })
            st.area_chart(confidence_data)
    else:
        st.error("Local Model File (`models/best_model.pkl`) not found. Please use the API button or upload the model.")