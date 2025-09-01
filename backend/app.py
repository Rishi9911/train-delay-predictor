from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import joblib
import os
from datetime import datetime
from flask_mail import Mail, Message 

# ---------------- Flask App Setup ----------------
app = Flask(__name__)
app.secret_key = '4087aec5b07d56a03909a669b1ae4864a7702d20a1e6078cf010186253ac7480'
CORS(app, supports_credentials=True)

# PostgreSQL config
DB_HOST = "localhost"
DB_NAME = "train_delay_db"
DB_USER = "postgres"
DB_PASS = "rishi@123"

# Load ML Model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_model.pkl")
model = joblib.load(MODEL_PATH)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

# ---------------- Flask-Login ----------------
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return User(user[0], user[1])
    return None

# ---------------- Flask-Mail Config ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rishichaudhari999@gmail.com'        # Replace
app.config['MAIL_PASSWORD'] = 'hzrr rfcb kage cqjg'     # Replace with App Password
app.config['MAIL_DEFAULT_SENDER'] = ('Train Delay Predictor', 'rishichaudhari999@gmail.com')

mail = Mail(app)

# ---------------- Register ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if username or email already exists
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"message": "Username or Email already exists."}), 409

        # Insert new user and return ID
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id",
                    (username, email, hashed_password))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        # Auto-login
        user_obj = User(user_id, username)
        login_user(user_obj)

        # Send Welcome Email
        try:
            msg = Message(
                subject="Welcome to Train Delay Predictor 🚆",
                recipients=[email],
                html=f"""
                <h2>Hello {username},</h2>
                <p>🎉 Congratulations! You have successfully registered on <b>Train Delay Predictor</b>.</p>
                <p>You can now log in with your username and password to:</p>
                <ul>
                    <li>Predict train delays</li>
                    <li>Track your history</li>
                    <li>Enjoy our AI-powered dashboard</li>
                </ul>
                <p>🔹 <a href="http://localhost:3000/">Click here to Login</a></p>
                <br>
                <p>Thanks for joining us!<br>🚆 Train Delay Predictor Team</p>
                """
            )
            mail.send(msg)
        except Exception as mail_err:
            print("Email sending failed:", mail_err)

        return jsonify({"message": "User registered successfully.", "username": username}), 201

    except Exception as e:
        print("Registration error:", e)
        return jsonify({"message": "Error occurred"}), 500

# ---------------- Login ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1])
            login_user(user_obj)
            return jsonify({"message": "Login successful.", "username": user[1]}), 200
        else:
            return jsonify({"message": "Invalid username or password"}), 401

    except Exception as e:
        print("Login error:", e)
        return jsonify({"message": "Error occurred"}), 500

# ---------------- Profile ----------------
@app.route("/profile", methods=["GET"])
@login_required
def profile():
    return jsonify({"username": current_user.username})

# ---------------- Logout ----------------
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully."}), 200

# ---------------- Predict ----------------
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    data = request.get_json()
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d')
        features = {
            'Temperature': float(data['temperature']),
            'Rain': int(data['rain']),
            'Fog': int(data['fog']),
            'Visibility': float(data['visibility']),
            'WindSpeed': float(data['windspeed']),
            'DayOfWeek': date.weekday(),
            'Month': date.month,
            'DayOfYear': date.timetuple().tm_yday,
            'Year': date.year,
            'Day': date.day
        }

        df = pd.DataFrame([features])
        predicted_delay = model.predict(df)[0]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO predictions
            (user_id, date, temperature, rain, fog, visibility, windspeed, predicted_delay)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            current_user.id, data['date'], features['Temperature'], features['Rain'],
            features['Fog'], features['Visibility'], features['WindSpeed'], float(predicted_delay)
        ))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"predicted_delay": round(float(predicted_delay), 2)})
    except Exception as e:
        print("[PREDICT] Error:", e)
        return jsonify({"error": "Prediction failed"}), 500

# ---------------- History ----------------
@app.route("/history", methods=["GET"])
@login_required
def history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT date, temperature, rain, fog, visibility, windspeed, predicted_delay
            FROM predictions
            WHERE user_id = %s
            ORDER BY id DESC
        """, (current_user.id,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        result = [
            {
                "date": r[0],
                "temperature": r[1],
                "rain": r[2],
                "fog": r[3],
                "visibility": r[4],
                "windspeed": r[5],
                "predicted_delay": r[6]
            }
            for r in rows
        ]

        return jsonify(result)

    except Exception as e:
        print("[HISTORY] Error:", e)
        return jsonify({"error": "Failed to fetch history"}), 500

if __name__ == "__main__":
    app.run(debug=True)
