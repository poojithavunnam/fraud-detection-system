from flask import Flask, jsonify, render_template, redirect, session, request
from flask_cors import CORS
from datetime import timedelta
import os

from database import init_db
from routes.auth_routes import auth_bp
from routes.transaction_routes import transaction_bp
from routes.dashboard_routes import dashboard_bp

# ---------------- APP SETUP ----------------
app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "banking_fraud_detection_secure_key_123")

CORS(app)

# ---------------- SESSION CONFIGURATION ----------------
# professional session security settings
app.config.update(
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False, # Set to True in production with HTTPS
)

# ---------------- DATABASE INIT ----------------
with app.app_context():
    init_db()

# ---------------- REGISTER BLUEPRINTS ----------------
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(transaction_bp, url_prefix='/api/transactions')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

# ---------------- MIDDLEWARE ----------------
@app.before_request
def make_session_permanent():
    session.permanent = True

# ---------------- UI ROUTES ----------------
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/login")
def login_page():
    if "user" in session:
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard_page():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

# ---------------- ERROR HANDLERS ----------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)