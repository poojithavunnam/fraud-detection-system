from flask import Blueprint, request, jsonify, session
from database import get_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Handles user login and automatic registration for demo purposes.
    Ensures secure session creation.
    """
    try:
        data = request.json
        if not data or "email" not in data or "password" not in data:
            return jsonify({"error": "Email and password are required"}), 400

        email = data["email"].strip().lower()
        password = data["password"]

        if not email or not password:
            return jsonify({"error": "Valid credentials are required"}), 400

        conn = get_db()
        
        # Check if user exists
        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        if not user:
            # Auto-register for easy demo access
            conn.execute(
                "INSERT INTO users(email, password) VALUES(?,?)",
                (email, password)
            )
            conn.commit()
        else:
            # Check password (simple comparison for demo)
            if user["password"] != password:
                return jsonify({"error": "Invalid credentials"}), 401

        # Establish session
        session.clear()
        session["user"] = email

        return jsonify({
            "status": "success",
            "message": "Authentication successful",
            "user": email
        })

    except Exception as e:
        return jsonify({"error": "An internal error occurred", "details": str(e)}), 500


@auth_bp.route("/logout")
def logout():
    """
    Ends the current user session.
    """
    session.clear()
    return jsonify({"status": "success", "message": "Successfully logged out"})