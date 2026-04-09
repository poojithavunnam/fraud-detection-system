from flask import Blueprint, jsonify, session
from database import get_db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/stats")
def stats():
    """
    Fetches aggregate statistics for the user's transactions.
    """
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db()

        # Get total and fraud counts
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN fraud = 1 THEN 1 ELSE 0 END) as fraud,
                AVG(amount) as avg_amount
            FROM transactions 
            WHERE email=?
        """, (session["user"],)).fetchone()

        total = stats["total"] or 0
        fraud = stats["fraud"] or 0
        avg_amount = stats["avg_amount"] or 0

        # Get location distribution
        locations = conn.execute("""
            SELECT location, COUNT(*) as count 
            FROM transactions 
            WHERE email=? 
            GROUP BY location 
            ORDER BY count DESC 
            LIMIT 5
        """, (session["user"],)).fetchall()

        location_data = {row["location"]: row["count"] for row in locations}

        return jsonify({
            "status": "success",
            "total_transactions": total,
            "fraud_detected": fraud,
            "safe_transactions": total - fraud,
            "avg_transaction_amount": round(avg_amount, 2),
            "top_locations": location_data
        })

    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500