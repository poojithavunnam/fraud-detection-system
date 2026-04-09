from flask import Blueprint, request, jsonify, session
from database import get_db
import pandas as pd
import io

transaction_bp = Blueprint("transaction", __name__)

def detect_fraud(amount):
    """
    Simple rule engine for fraud detection.
    In a real system, this would be a machine learning model.
    """
    # Flag transactions over 10,000 as high risk
    if amount > 10000:
        return 1
    return 0

@transaction_bp.route("/upload", methods=["POST"])
def upload_transactions():
    """
    Handles CSV upload, processes transactions, and stores results.
    """
    if "user" not in session:
        return jsonify({"error": "Authentication required"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files["file"]
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Only CSV files are allowed"}), 400

    try:
        # Read CSV directly from memory
        content = file.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(content))

        # Basic validation
        required_columns = ["amount", "location"]
        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": f"CSV must contain columns: {', '.join(required_columns)}"}), 400

        conn = get_db()
        
        # Clear existing data for this user for a fresh analysis
        conn.execute("DELETE FROM transactions WHERE email=?", (session["user"],))

        total_count = 0
        fraud_count = 0
        location_data = {}

        for _, row in df.iterrows():
            amount = float(row["amount"])
            location = str(row["location"])
            
            fraud = detect_fraud(amount)
            
            if fraud:
                fraud_count += 1
            
            total_count += 1
            
            # Aggregate location data for insights
            location_data[location] = location_data.get(location, 0) + 1

            conn.execute(
                "INSERT INTO transactions(email, amount, location, fraud) VALUES (?,?,?,?)",
                (session["user"], amount, location, fraud)
            )

        conn.commit()

        # Prepare rich response for the dashboard
        result = {
            "status": "success",
            "total": total_count,
            "fraud": fraud_count,
            "safe": total_count - fraud_count,
            "fraud_rate": round((fraud_count / total_count) * 100, 2) if total_count > 0 else 0,
            "locations": location_data
        }
        
        # Store latest result in session for display
        session["latest_result"] = result

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": "Failed to process file", "details": str(e)}), 500

@transaction_bp.route("/list", methods=["GET"])
def list_transactions():
    """
    Returns a list of transactions for the current user.
    Optional query parameter: fraud (0 or 1)
    """
    if "user" not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    fraud_filter = request.args.get("fraud")
    
    try:
        conn = get_db()
        if fraud_filter is not None:
            txs = conn.execute(
                "SELECT id, amount, location, fraud FROM transactions WHERE email=? AND fraud=? ORDER BY id DESC",
                (session["user"], fraud_filter)
            ).fetchall()
        else:
            txs = conn.execute(
                "SELECT id, amount, location, fraud FROM transactions WHERE email=? ORDER BY id DESC",
                (session["user"],)
            ).fetchall()
            
        return jsonify({
            "status": "success",
            "transactions": [dict(tx) for tx in txs]
        })
    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500