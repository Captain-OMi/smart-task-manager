# This file is the main entry point of the Smart Task Manager Flask project, responsible for creating the Flask app, loading environment settings, registering authentication/task/admin route blueprints, configuring sessions, and starting the local development server.

import os
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask.json.provider import DefaultJSONProvider

from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.task import task_bp


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


class DateTimeJSONProvider(DefaultJSONProvider):
    def default(self, value):
        if isinstance(value, (datetime, date)):
            return value.isoformat()

        return super().default(value)


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "development_secret_key_change_me")
    app.json = DateTimeJSONProvider(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(admin_bp)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("error.html", code=500, message="Server error. Please try again."), 500

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
