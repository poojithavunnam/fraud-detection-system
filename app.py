from flask import Flask, jsonify, render_template, redirect, session, request
from flask_cors import CORS
from datetime import timedelta

from database import init_db
from routes.auth_routes import auth_bp
from routes.transaction_routes import transaction_bp
from routes.dashboard_routes import dashboard_bp


# ---------------- APP SETUP ----------------
app = Flask(__name__, template_folder="templates")
app.secret_key = "secret123"

CORS(app)

# ---------------- SESSION SECURITY FIX ----------------
# prevents old password/session reuse
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ---------------- DATABASE INIT ----------------
init_db()

# ---------------- REGISTER BLUEPRINTS ----------------
app.register_blueprint(auth_bp)
app.register_blueprint(transaction_bp)
app.register_blueprint(dashboard_bp)


# ---------------- AUTO SESSION CLEANER ----------------
# clears old sessions automatically
@app.before_request
def clear_invalid_session():

    allowed_routes = ["login_page", "login", "static"]

    if request.endpoint not in allowed_routes:
        if "user" not in session:
            session.clear()


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return redirect("/login")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard_page():

    # dashboard protection
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


@app.route("/results")
def results():

    # block unauthorized access
    if "user" not in session:
        session.clear()
        return jsonify({"message": "Unauthorized"}), 401

    if "latest_result" not in session:
        return jsonify({"message": "No analysis yet"}), 204

    return jsonify(session["latest_result"])


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)