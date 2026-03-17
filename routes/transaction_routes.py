from flask import Blueprint, request, jsonify, session
from database import get_db
import pandas as pd

transaction_bp = Blueprint("transaction", __name__)


def detect_fraud(amount):
    # SIMPLE RULE ENGINE
    if amount > 10000:
        return 1
    return 0


@transaction_bp.route("/upload", methods=["POST"])
def upload_transactions():

    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    file = request.files["file"]
    df = pd.read_csv(file)

    conn = get_db()

    # 🔥 FIX: clear old data
    conn.execute("DELETE FROM transactions WHERE email=?", (session["user"],))

    total = 0
    fraud_count = 0

    for _, row in df.iterrows():

        amount = row["amount"]
        location = row["location"]

        fraud = 1 if amount > 10000 else 0

        if fraud:
            fraud_count += 1

        total += 1

        conn.execute(
            "INSERT INTO transactions(email, amount, location, fraud) VALUES (?,?,?,?)",
            (session["user"], amount, location, fraud)
        )

    conn.commit()

    # store latest result
    session["latest_result"] = {
        "total": total,
        "fraud": fraud_count,
        "safe": total - fraud_count
    }

    return jsonify(session["latest_result"])