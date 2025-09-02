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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# 🔹 Cookie settings for cross-site login
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True  # Render uses HTTPS

# 🔹 Secret + frontend origin
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://traindelaypredictor.netlify.app")

# 🔹 Enable CORS (credentials allowed)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": [FRONTEND_URL]}}
)

# ---------------- Database config ----------------
DATABASE_URL = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "train_delay_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")


def get_db_connection():
    try:
        if DATABASE_URL:
            return psycopg2.connect(DATABASE_URL)
        else:
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
    except Exception as e:
        print("[DB CONNECT] Error connecting to DB:", e)
        raise


# ---------------- ML Model ----------------
MODEL_PATH = os.path.join(BASE_DIR, "best_model.pkl")
try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded from", MODEL_PATH)
except Exception as e:
    print("Model load failed:", e)
    model = None


# ---------------- Flask-Login ----------------
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return User(user[0], user[1])
    except Exception as e:
        print("[LOAD_USER] Error:", e)
    return None


# ---------------- Mail Config ----------------
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", None)
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", None)
app.config['MAIL_DEFAULT_SENDER'] = (
    os.getenv("MAIL_DEFAULT_SENDER_NAME", "Train Delay Predictor"),
    os.getenv("MAIL_DEFAULT_SENDER_EMAIL", app.config['MAIL_USERNAME'])
)

mail = Mail(app)

# ---------------- Health route ----------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ---------------- Root route ----------------
@app.route("/")
def root():
    return jsonify({"message": "Train Delay Predictor API is running!"})


# ---------------- Force OPTIONS handler ----------------
@app.route("/register", methods=["OPTIONS"])
@app.route("/login", methods=["OPTIONS"])
@app.route("/profile", methods=["OPTIONS"])
@app.route("/predict", methods=["OPTIONS"])
@app.route("/history", methods=["OPTIONS"])
@app.route("/logout", methods=["OPTIONS"])
def options_handler():
    return "", 200


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

        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"message": "Username or Email already exists."}), 409

        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id",
            (username, email, hashed_password)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        user_obj = User(user_id, username)
        login_user(user_obj)

        try:
            msg = Message(
                subject="Welcome to Train Delay Predictor 🚆",
                recipients=[email],
                html=f"""
                <h2>Hello {username},</h2>
                <p>🎉 Congratulations! You have successfully registered on <b>Train Delay Predictor</b>.</p>
                <p><a href="{FRONTEND_URL}">Click here to Login</a></p>
                """
            )
            if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
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
    if model is None:
        return jsonify({"error": "Model not available on server"}), 500

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
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
