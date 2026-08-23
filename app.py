import json
import os
import re
import sqlite3
from functools import wraps
from pathlib import Path
from config.settings import Config
from database.db import get_db_connection, init_db
import random_responses

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

app.config.from_object(Config)

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "SECRET_KEY is not configured. Copy .env.example to .env and set SECRET_KEY."
    )

# -----------------------------
# Cache Control
# -----------------------------
@app.after_request
def add_no_cache_headers(response):
    """
    Prevent browsers from serving cached authenticated pages
    when Back/Forward buttons are used.
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



# -----------------------------
# Chatbot Data
# -----------------------------
def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        print(f"Loaded '{path.name}' successfully!")
        return json.load(f)


response_data = load_json(Config.BOT_DATA_PATH)

# -----------------------------
# Authentication Decorator
# -----------------------------
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required."}), 401
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view

# -----------------------------
# Chatbot Logic
# -----------------------------
def get_response(input_string):
    input_string = (input_string or "").strip()

    if not input_string:
        return "Please type something so we can chat."

    split_message = re.split(r"\s+|[,;?!.-]\s*", input_string.lower())
    score_list = []

    for response in response_data:
        response_score = 0
        required_score = 0
        required_words = response.get("required_words", [])

        for word in split_message:
            if word in required_words:
                required_score += 1

        if required_score == len(required_words):
            for word in split_message:
                if word in response.get("user_input", []):
                    response_score += 1

        score_list.append(response_score)

    best_response = max(score_list, default=0)

    if best_response > 0:
        return response_data[score_list.index(best_response)]["bot_response"]

    return random_responses.random_string()

# ======================================================
# Routes
# ======================================================

# Landing route
@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

# Login page
@app.route("/login")
def login():
    if "user" in session:
        return redirect(url_for("home"))

    return render_template("login.html", error=request.args.get("error"))

# Login form submission
@app.route("/signin", methods=["POST"])
def signin():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT user,password,role FROM info WHERE user=?",
            (username,),
        ).fetchone()

    if user is None or not check_password_hash(user["password"], password):
        return render_template(
            "login.html",
            error="User ID or password is incorrect.",
        ), 401

    session.clear()
    session["user"] = user["user"]
    session["role"] = user["role"]

    return redirect(url_for("home"))

# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""

    if request.method == "POST":
        username = (request.form.get("user") or "").strip()
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        mobile = (request.form.get("mobile") or "").strip()
        password = request.form.get("password") or ""

        if not all([username, name, email, mobile, password]):
            error = "All fields are mandatory."

        elif len(password) < 8:
            error = "Password must be at least 8 characters long."

        else:
            try:
                with get_db_connection() as conn:
                    conn.execute(
                        """
                        INSERT INTO info(user,email,password,mobile,name)
                        VALUES(?,?,?,?,?)
                        """,
                        (
                            username,
                            email,
                            generate_password_hash(password),
                            mobile,
                            name,
                        ),
                    )
                    conn.commit()

                return redirect(
                    url_for(
                        "login",
                        error="Registration successful. Please log in.",
                    )
                )

            except sqlite3.IntegrityError:
                error = "Username or email already exists."

    return render_template("register.html", error=error)

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()

    response = redirect(url_for("login"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

# Chat page
@app.route("/app")
@login_required
def home():
    return render_template("index.html", username=session["user"])

# Chat API
@app.post("/api/chat")
@login_required
def chat():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message")

    if not isinstance(message, str):
        return jsonify({"error": "Message must be a string."}), 400

    message = message.strip()

    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if len(message) > 2000:
        return jsonify({"error": "Message is too long."}), 400

    return jsonify({"answer": get_response(message)})

# Health Check
@app.get("/health")
def health():
    return jsonify({"status": "ok"})

# ======================================================
# Run
# ======================================================
if __name__ == "__main__":
    init_db()
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")