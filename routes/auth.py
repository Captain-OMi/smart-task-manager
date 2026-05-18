# This file is used to handle authentication routes for the Smart Task Manager project, including user registration, login validation, session creation, role-based dashboard redirects, and logout session cleanup.

from functools import wraps

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from psycopg2.errors import UniqueViolation
from werkzeug.security import check_password_hash

from models.user import create_user, find_user_by_email


auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("auth.login"))

        if session.get("role") != "admin":
            flash("Admin access required.", "error")
            return redirect(url_for("task.dashboard"))

        return view(*args, **kwargs)

    return wrapped_view


@auth_bp.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") == "admin":
        return redirect(url_for("admin.admin_dashboard"))

    return redirect(url_for("task.dashboard"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name or not email or not password:
        flash("Name, email, and password are required.", "error")
        return redirect(url_for("auth.register"))

    if password != confirm_password:
        flash("Password and confirm password must match.", "error")
        return redirect(url_for("auth.register"))

    try:
        create_user(name, email, password)
    except UniqueViolation:
        flash("Email already registered. Please login.", "error")
        return redirect(url_for("auth.login"))

    flash("Registration successful. Please login.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    user = find_user_by_email(email)

    if not user or not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password.", "error")
        return redirect(url_for("auth.login"))

    session.clear()
    session["user_id"] = user["id"]
    session["name"] = user["name"]
    session["email"] = user["email"]
    session["role"] = user["role"]

    if user["role"] == "admin":
        return redirect(url_for("admin.admin_dashboard"))

    return redirect(url_for("task.dashboard"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/api/session")
def current_session():
    if "user_id" not in session:
        return jsonify({"logged_in": False})

    return jsonify(
        {
            "logged_in": True,
            "user": {
                "id": session["user_id"],
                "name": session["name"],
                "email": session["email"],
                "role": session["role"],
            },
        }
    )
