# This file is used during local setup or Railway deployment to initialize the Smart Task Manager PostgreSQL database by executing database/schema.sql before the Flask web service starts.

from pathlib import Path

from database.db import get_connection


def main():
    schema_path = Path(__file__).resolve().parent / "database" / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")

    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(schema_sql)
        print("Database schema initialized successfully.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
