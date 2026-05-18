# This file is used to manage PostgreSQL database connectivity for the Smart Task Manager Flask app by reading database settings from environment variables and providing reusable connection helpers for models and routes.

import os
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise RuntimeError("DB_PASSWORD is missing. Please set it in the project .env file.")

    return psycopg2.connect(
        host=os.getenv("PGHOST") or os.getenv("DB_HOST", "localhost"),
        port=os.getenv("PGPORT") or os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("PGDATABASE") or os.getenv("DB_NAME", "smart_task_manager"),
        user=os.getenv("PGUSER") or os.getenv("DB_USER", "postgres"),
        password=db_password,
        cursor_factory=RealDictCursor,
    )


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)

                if fetch_one:
                    return cursor.fetchone()

                if fetch_all:
                    return cursor.fetchall()

                return None
    finally:
        connection.close()
