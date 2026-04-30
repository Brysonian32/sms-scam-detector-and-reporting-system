import sqlite3
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)

def get_db():
    conn = sqlite3.connect("scams.db")
    conn.row_factory = sqlite3.Row
    return conn

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE email = ? OR username = ?", (email, username)
        ).fetchone()

        if existing:
            flash("Username or email already exists.", "error")
            db.close()
            return render_template("register.html")

        hashed = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed)
        )
        db.commit()
        db.close()
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        db.close()

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["is_admin"] = user["is_admin"]

        flash(f"Welcome back, {user['username']}!", "success")

        if user["is_admin"]:
            return redirect(url_for("admin.dashboard"))

        return redirect(url_for("home"))

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))