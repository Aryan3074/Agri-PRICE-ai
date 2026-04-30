from fastapi import FastAPI
from pydantic import BaseModel
import requests
import joblib
import numpy as np
import pandas as pd

# 1. Initialize FastAPI app
app = FastAPI(title="AgriPrice AI API")
API_KEY = "29586ccbe4150af4b4af0971da3244ae"

class PredictionRequest(BaseModel):
    month: int
    yesterday_price: float
    seven_day_avg: float
    temp: float        # New
    humidity: float    # New
    rainfall: float
    
@app.post("/predict")
def predict(data: PredictionRequest):
    try:
        # Load fresh model every time during testing to see changes
        model = joblib.load("models/best_model.pkl")
        
        # Ensure column order is EXACTLY as it was in training
        cols = ['month', 'yesterday_price', 'seven_day_avg', 'temp', 'humidity', 'rainfall']
        input_data = pd.DataFrame([[
            data.month, data.yesterday_price, data.seven_day_avg,
            data.temp, data.humidity, data.rainfall
        ]], columns=cols)
        
        prediction = model.predict(input_data)[0]
        return {"prediction": round(float(prediction), 2)}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/")
def home():
    return {"message": "Agri Price AI API is Live"}

def get_live_weather(city="Nagpur"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        temp = response['main']['temp']
        humidity = response['main']['humidity']
        weather_desc = response['weather'][0]['description']
        return {"temp": temp, "humidity": humidity, "desc": weather_desc}
    except Exception:
        return {"temp": 25, "humidity": 50, "desc": "clear sky"}

@app.get("/weather/{city}")
def weather_endpoint(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    
    # Check if the OpenWeather API request was successful
    if response.status_code == 200:
        data = response.json()
        return {
            "temp": data['main']['temp'],
            "humidity": data['main']['humidity'],
            "desc": data['weather'][0]['description']
        }
    else:
        # Fallback data if city is not found or API fails
        return {"temp": 25.0, "humidity": 50, "desc": "location not found"}

@app.post("/predict")
async def predict_price(data: PredictionRequest):
    try:
        # Convert input to DataFrame for the scaler
        input_data = pd.DataFrame([{
            'month_sin': np.sin(2 * np.pi * data.month / 12),
            'month_cos': np.cos(2 * np.pi * data.month / 12),
            'day_of_week': data.day_of_week,
            'price_lag_1': data.price_lag_1,
            'price_lag_7': data.price_lag_7,
            'rolling_mean_7': data.rolling_mean_7
        }])
        
        # Scale the inputs using the saved scaler
        scaled_features = scaler.transform(input_data)
        
        # Generate prediction
        prediction = model.predict(scaled_features)
        
        return {
            "status": "success",
            "predicted_price": round(float(prediction[0]), 2),
            "unit": "INR per Quintal"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Agri Price AI API is Live."}
# 2. Load the saved model and scaler artifacts
try:
    artifacts = joblib.load("models/best_model.pkl")
    model = artifacts['model']
    scaler = artifacts['scaler']
except Exception as e:
    print(f"Error loading model: {e}")

# 3. Define the Input Data Schema
class PredictionRequest(BaseModel):
    month: int
    day_of_week: int
    price_lag_1: float
    price_lag_7: float
    rolling_mean_7: float

# 4. Define the Prediction Endpoint


