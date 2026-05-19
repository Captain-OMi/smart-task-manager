# This file is used to keep all user-related database operations for the Smart Task Manager project, including creating new users with hashed passwords, finding users during login, listing users for admin screens, and deleting users safely from PostgreSQL.

from werkzeug.security import generate_password_hash

from database.db import execute_query


def create_user(name, email, password, role="user", password_already_hashed=False):
    password_hash = password if password_already_hashed else generate_password_hash(password)

    query = """
        INSERT INTO users (name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        RETURNING id, name, email, role, created_at;
    """
    return execute_query(query, (name, email, password_hash, role), fetch_one=True)


def find_user_by_email(email):
    query = """
        SELECT id, name, email, password_hash, role, created_at
        FROM users
        WHERE email = %s;
    """
    return execute_query(query, (email,), fetch_one=True)


def find_user_by_id(user_id):
    query = """
        SELECT id, name, email, role, created_at
        FROM users
        WHERE id = %s;
    """
    return execute_query(query, (user_id,), fetch_one=True)


def get_all_users():
    query = """
        SELECT id, name, email, role, created_at
        FROM users
        ORDER BY created_at DESC;
    """
    return execute_query(query, fetch_all=True)


def delete_user(user_id):
    query = """
        DELETE FROM users
        WHERE id = %s
        RETURNING id;
    """
    return execute_query(query, (user_id,), fetch_one=True)
