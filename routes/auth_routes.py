from flask import Blueprint, request, jsonify, session
from database import get_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json
    email = data["email"]
    password = data["password"]

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    ).fetchone()

    if not user:
        conn.execute(
            "INSERT INTO users(email,password) VALUES(?,?)",
            (email, password)
        )
        conn.commit()

    session["user"] = email

    return jsonify({"message": "Login Success"})


@auth_bp.route("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})