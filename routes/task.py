# This file is used to handle normal user task workflows for the Smart Task Manager project, including the dashboard page and REST API endpoints for listing, adding, updating, completing, and deleting the logged-in user's own tasks.

from flask import Blueprint, jsonify, render_template, request, session

from models.task import create_task, delete_task, get_tasks_by_user, mark_task_completed, update_task
from routes.auth import login_required


task_bp = Blueprint("task", __name__)


@task_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@task_bp.route("/tasks")
@login_required
def list_tasks():
    tasks = get_tasks_by_user(session["user_id"])
    return jsonify({"tasks": tasks})


@task_bp.route("/task/add", methods=["POST"])
@login_required
def add_task():
    data = request.get_json(silent=True) or request.form
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    status = data.get("status", "pending")

    if not title:
        return jsonify({"error": "Task title is required."}), 400

    task = create_task(session["user_id"], title, description, status)
    return jsonify({"message": "Task created successfully.", "task": task}), 201


@task_bp.route("/task/update", methods=["PUT", "POST"])
@login_required
def edit_task():
    data = request.get_json(silent=True) or request.form
    task_id = data.get("id")
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    status = data.get("status", "pending")

    if not task_id or not title:
        return jsonify({"error": "Task id and title are required."}), 400

    task = update_task(task_id, session["user_id"], title, description, status)
    if not task:
        return jsonify({"error": "Task not found or permission denied."}), 404

    return jsonify({"message": "Task updated successfully.", "task": task})


@task_bp.route("/task/complete", methods=["PUT", "POST"])
@login_required
def complete_task():
    data = request.get_json(silent=True) or request.form
    task_id = data.get("id")

    if not task_id:
        return jsonify({"error": "Task id is required."}), 400

    task = mark_task_completed(task_id, session["user_id"])
    if not task:
        return jsonify({"error": "Task not found or permission denied."}), 404

    return jsonify({"message": "Task marked completed.", "task": task})


@task_bp.route("/task/delete", methods=["DELETE", "POST"])
@login_required
def remove_task():
    data = request.get_json(silent=True) or request.form
    task_id = data.get("id")

    if not task_id:
        return jsonify({"error": "Task id is required."}), 400

    deleted = delete_task(task_id, session["user_id"])
    if not deleted:
        return jsonify({"error": "Task not found or permission denied."}), 404

    return jsonify({"message": "Task deleted successfully."})
