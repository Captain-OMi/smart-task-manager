# This file is used to handle authentication routes for the Smart Task Manager project, including user registration, login validation, session creation, role-based dashboard redirects, and logout session cleanup.

from functools import wraps

import random

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from psycopg2.errors import UniqueViolation
from werkzeug.security import check_password_hash, generate_password_hash

from models.registration import (
    delete_expired_pending_registrations,
    delete_pending_registration,
    find_pending_registration,
    save_pending_registration,
)
from models.user import create_user, find_user_by_email
from utils.email_service import send_registration_otp


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

    if find_user_by_email(email):
        flash("Email already registered. Please login.", "error")
        return redirect(url_for("auth.login"))

    otp = f"{random.randint(100000, 999999)}"
    password_hash = generate_password_hash(password)
    otp_hash = generate_password_hash(otp)

    try:
        delete_expired_pending_registrations()
        save_pending_registration(name, email, password_hash, otp_hash)
        send_registration_otp(email, name, otp)
    except UniqueViolation:
        flash("Email already registered. Please login.", "error")
        return redirect(url_for("auth.login"))
    except RuntimeError as error:
        flash(str(error), "error")
        return redirect(url_for("auth.register"))
    except Exception:
        flash("Unable to send verification email. Please check SMTP email settings and try again.", "error")
        return redirect(url_for("auth.register"))

    session["pending_registration_email"] = email
    flash("Verification code sent to your email. Please enter it to complete registration.", "success")
    return redirect(url_for("auth.verify_otp"))


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    email = session.get("pending_registration_email", "")

    if request.method == "GET":
        return render_template("verify_otp.html", email=email)

    email = request.form.get("email", "").strip().lower()
    otp = request.form.get("otp", "").strip()

    if not email or not otp:
        flash("Email and verification code are required.", "error")
        return redirect(url_for("auth.verify_otp"))

    pending = find_pending_registration(email)
    if not pending or not check_password_hash(pending["otp_hash"], otp):
        flash("Invalid or expired verification code.", "error")
        return redirect(url_for("auth.verify_otp"))

    try:
        create_user(pending["name"], pending["email"], pending["password_hash"], password_already_hashed=True)
    except UniqueViolation:
        flash("Email already registered. Please login.", "error")
        return redirect(url_for("auth.login"))

    delete_pending_registration(email)
    session.pop("pending_registration_email", None)
    flash("Account verified and created successfully. Please login.", "success")
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
