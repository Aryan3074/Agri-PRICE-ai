import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def train_model():
    print("--- 1. Generating Real-World Synthetic Data ---")
    n_rows = 1000
    # Generate data that mimics your dashboard inputs
    data = {
        'month': np.random.randint(1, 13, n_rows),
        'yesterday_price': np.random.uniform(1500, 3000, n_rows),
        'seven_day_avg': np.random.uniform(1500, 3000, n_rows),
        'temp': np.random.uniform(10, 45, n_rows),
        'humidity': np.random.uniform(20, 90, n_rows),
        'rainfall': np.random.uniform(0, 200, n_rows)
    }
    df = pd.DataFrame(data)
    
    # Logic: Price increases with yesterday's price, but drops if it's too hot/dry
    df['Modal_Price'] = (
        (df['yesterday_price'] * 0.8) + 
        (df['seven_day_avg'] * 0.2) + 
        (df['rainfall'] * 2.5) - 
        (df['temp'] * 5) + 
        np.random.normal(0, 15, n_rows)
    )

    features = ['month', 'yesterday_price', 'seven_day_avg', 'temp', 'humidity', 'rainfall']
    X, y = df[features], df['Modal_Price']
    
    print("--- 2. Training Random Forest Regressor ---")
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X, y)
    
    if not os.path.exists('models'): os.makedirs('models')
    
    # Save as a single object to ensure API can read it easily
    joblib.dump(model, 'models/best_model.pkl')
    print("✅ SUCCESS: Dynamic model ready at models/best_model.pkl")

if __name__ == "__main__":
    train_model()