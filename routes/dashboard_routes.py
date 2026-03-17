from flask import Blueprint, jsonify, session
from database import get_db

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/stats")
def stats():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) as c FROM transactions WHERE email=?",
        (session["user"],)
    ).fetchone()["c"]

    fraud = conn.execute(
        "SELECT COUNT(*) as c FROM transactions WHERE fraud=1 AND email=?",
        (session["user"],)
    ).fetchone()["c"]

    return jsonify({
        "total_transactions": total,
        "fraud_detected": fraud
    })