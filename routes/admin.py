# This file is used to handle admin-only workflows for the Smart Task Manager project, including the admin dashboard, viewing all users and tasks, deleting users, and deleting any task across the system.

from flask import Blueprint, jsonify, render_template, request, session

from models.task import admin_delete_task, get_all_tasks_with_users
from models.user import delete_user, get_all_users
from routes.auth import admin_required


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html")


@admin_bp.route("/users")
@admin_required
def list_users():
    users = get_all_users()
    return jsonify({"users": users})


@admin_bp.route("/admin/tasks")
@admin_required
def list_all_tasks():
    tasks = get_all_tasks_with_users()
    return jsonify({"tasks": tasks})


@admin_bp.route("/user/delete", methods=["DELETE", "POST"])
@admin_required
def remove_user():
    data = request.get_json(silent=True) or request.form
    user_id = data.get("id")

    if not user_id:
        return jsonify({"error": "User id is required."}), 400

    if int(user_id) == int(session["user_id"]):
        return jsonify({"error": "Admin cannot delete the currently logged-in account."}), 400

    deleted = delete_user(user_id)
    if not deleted:
        return jsonify({"error": "User not found."}), 404

    return jsonify({"message": "User deleted successfully."})


@admin_bp.route("/admin/task/delete", methods=["DELETE", "POST"])
@admin_required
def remove_any_task():
    data = request.get_json(silent=True) or request.form
    task_id = data.get("id")

    if not task_id:
        return jsonify({"error": "Task id is required."}), 400

    deleted = admin_delete_task(task_id)
    if not deleted:
        return jsonify({"error": "Task not found."}), 404

    return jsonify({"message": "Task deleted successfully."})
