from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

df = pd.read_csv('weather.csv')
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])

df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['DayOfYear'] = df['Date'].dt.dayofyear
df['DayOfWeek'] = df['Date'].dt.dayofweek

X = df[['Temperature', 'Rain', 'Fog', 'Visibility', 'WindSpeed', 'DayOfWeek', 'Month', 'DayOfYear', 'Year', 'Day']]
y = df['Delay']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=72)

models = {
    'Random Forest': RandomForestRegressor(n_estimators=160, random_state=72),
    'Linear Regression': LinearRegression(),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=160, random_state=72),
}

model_performance = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    model_performance[name] = (mse, r2)

best_model_name = min(model_performance, key=lambda k: (model_performance[k][0], -model_performance[k][1]))
best_model = models[best_model_name]

def predict_delay(temperature, rain, fog, visibility, windspeed, date_str):
    date = datetime.strptime(date_str, '%d-%m-%Y')
    features = {
        'Temperature': temperature,
        'Rain': rain,
        'Fog': fog,
        'Visibility': visibility,
        'WindSpeed': windspeed,
        'DayOfWeek': date.weekday(),
        'Month': date.month,
        'DayOfYear': date.timetuple().tm_yday,
        'Year': date.year,
        'Day': date.day
    }
    features_df = pd.DataFrame([features])
    return best_model.predict(features_df)[0]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        temperature = float(request.form['temperature'])
        rain = int(request.form['rain'])
        fog = int(request.form['fog'])
        visibility = float(request.form['visibility'])
        windspeed = float(request.form['windspeed'])
        date_str = request.form['date']

        predicted_delay = predict_delay(temperature, rain, fog, visibility, windspeed, date_str)
        return render_template('index.html', prediction=predicted_delay, date=date_str)
    except Exception as e:
        logging.error("Error during prediction", exc_info=True)
        return render_template('index.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)