from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    if "user" in session:
        return redirect(url_for("home"))

    return render_template("login.html", error=request.args.get("error"))


@auth_bp.route("/signin", methods=["POST"])
def signin():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT user, password, role FROM info WHERE user = ?",
            (username,),
        ).fetchone()

    if user is None or not check_password_hash(user["password"], password):
        return (
            render_template(
                "login.html",
                error="User ID or password is incorrect.",
            ),
            401,
        )

    session.clear()
    session["user"] = user["user"]
    session["role"] = user["role"]

    return redirect(url_for("home"))


@auth_bp.route("/register", methods=["GET", "POST"])
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
                        INSERT INTO info (user, email, password, mobile, name)
                        VALUES (?, ?, ?, ?, ?)
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
                        "auth.login",
                        error="Registration successful. Please log in.",
                    )
                )

            except sqlite3.IntegrityError:
                error = "Username or email already exists."

    return render_template("register.html", error=error)


# ✅ Logout now matches the POST form in index.html
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()

    response = redirect(url_for("auth.login"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response