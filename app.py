import os

from flask import Flask, jsonify, redirect, render_template, session, url_for

from config.settings import Config
from database.db import init_db
from routes.auth import auth_bp
from routes.chat import chat_bp

# --------------------------------
# Flask App
# --------------------------------
app = Flask(__name__)
app.config.from_object(Config)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "SECRET_KEY is not configured. Copy .env.example to .env and set SECRET_KEY."
    )

# --------------------------------
# Prevent cached pages after logout
# --------------------------------
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# =====================================================
# Routes
# =====================================================

# Landing page
@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("home"))
    return redirect(url_for("auth.login"))


# Protected chat page
@app.route("/app")
def home():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    return render_template("index.html", username=session["user"])


# Health check
@app.get("/health")
def health():
    return jsonify({"status": "ok"})


# =====================================================
# Run
# =====================================================
if __name__ == "__main__":
    init_db()
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")