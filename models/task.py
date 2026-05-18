# This file is used to keep all task-related database operations for the Smart Task Manager project, including creating, reading, updating, completing, and deleting tasks while keeping every task connected to its owner user.

from database.db import execute_query


def create_task(user_id, title, description, status="pending"):
    query = """
        INSERT INTO tasks (user_id, title, description, status)
        VALUES (%s, %s, %s, %s)
        RETURNING id, user_id, title, description, status, created_at, updated_at;
    """
    return execute_query(query, (user_id, title, description, status), fetch_one=True)


def get_tasks_by_user(user_id):
    query = """
        SELECT id, user_id, title, description, status, created_at, updated_at
        FROM tasks
        WHERE user_id = %s
        ORDER BY created_at DESC;
    """
    return execute_query(query, (user_id,), fetch_all=True)


def get_all_tasks_with_users():
    query = """
        SELECT
            tasks.id,
            tasks.user_id,
            tasks.title,
            tasks.description,
            tasks.status,
            tasks.created_at,
            tasks.updated_at,
            users.name AS user_name,
            users.email AS user_email
        FROM tasks
        JOIN users ON users.id = tasks.user_id
        ORDER BY tasks.created_at DESC;
    """
    return execute_query(query, fetch_all=True)


def update_task(task_id, user_id, title, description, status):
    query = """
        UPDATE tasks
        SET title = %s,
            description = %s,
            status = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND user_id = %s
        RETURNING id, user_id, title, description, status, created_at, updated_at;
    """
    return execute_query(query, (title, description, status, task_id, user_id), fetch_one=True)


def mark_task_completed(task_id, user_id):
    query = """
        UPDATE tasks
        SET status = 'completed',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND user_id = %s
        RETURNING id, user_id, title, description, status, created_at, updated_at;
    """
    return execute_query(query, (task_id, user_id), fetch_one=True)


def delete_task(task_id, user_id):
    query = """
        DELETE FROM tasks
        WHERE id = %s AND user_id = %s
        RETURNING id;
    """
    return execute_query(query, (task_id, user_id), fetch_one=True)


def admin_delete_task(task_id):
    query = """
        DELETE FROM tasks
        WHERE id = %s
        RETURNING id;
    """
    return execute_query(query, (task_id,), fetch_one=True)
