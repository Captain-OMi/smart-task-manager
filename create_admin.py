# This file is used as a command-line helper for the Smart Task Manager project to create a new admin account or upgrade an existing registered user to admin role without manually writing SQL commands in PostgreSQL.

from getpass import getpass

from werkzeug.security import generate_password_hash

from database.db import execute_query
from models.user import find_user_by_email


def update_user_to_admin(email):
    query = """
        UPDATE users
        SET role = 'admin'
        WHERE email = %s
        RETURNING id, name, email, role;
    """
    return execute_query(query, (email,), fetch_one=True)


def create_admin_user(name, email, password):
    password_hash = generate_password_hash(password)
    query = """
        INSERT INTO users (name, email, password_hash, role)
        VALUES (%s, %s, %s, 'admin')
        RETURNING id, name, email, role;
    """
    return execute_query(query, (name, email, password_hash), fetch_one=True)


def main():
    print("Smart Task Manager - Admin Account Setup")
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password: ")
    confirm_password = getpass("Confirm password: ")

    if not name or not email or not password:
        print("Name, email, and password are required.")
        return

    if password != confirm_password:
        print("Password and confirm password do not match.")
        return

    existing_user = find_user_by_email(email)
    if existing_user:
        admin = update_user_to_admin(email)
        print(f"Existing user upgraded to admin: {admin['email']}")
        return

    admin = create_admin_user(name, email, password)
    print(f"New admin user created: {admin['email']}")


if __name__ == "__main__":
    main()
