<!-- This file is used as the main project guide for the Smart Task Manager application, explaining the project purpose, folder structure, required software, setup steps, database creation, local run commands, API endpoints, admin workflow, and deployment notes. -->

# Smart Task Manager

Smart Task Manager is a Flask, PostgreSQL, HTML, CSS, and JavaScript project for managing user tasks with authentication and role-based admin controls.

## Features

- User registration and login
- Email OTP verification before account creation
- Secure password hashing
- Session-based authentication
- User dashboard for task CRUD operations
- Admin dashboard for managing all users and tasks
- PostgreSQL relational database
- REST API endpoints returning JSON
- Railway-ready Flask structure

## Required Software

- Python 3.11 or newer
- PostgreSQL
- Git
- VS Code or any code editor

## Folder Structure

```text
smart-task-manager/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── database/
│   ├── __init__.py
│   ├── db.py
│   └── schema.sql
├── models/
│   ├── __init__.py
│   ├── task.py
│   └── user.py
├── routes/
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   └── task.py
├── static/
│   ├── script.js
│   └── style.css
└── templates/
    ├── admin_dashboard.html
    ├── base.html
    ├── dashboard.html
    ├── error.html
    ├── login.html
    └── register.html
```

## Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a real `.env` file by copying `.env.example`, then update the PostgreSQL password and secret key.

For OTP email verification, set `RESEND_API_KEY` and `RESEND_FROM_EMAIL` in production. SMTP `MAIL_*` values are also supported for local experiments, but Resend is recommended for Railway deployments.

## Database Setup

Create a PostgreSQL database named `smart_task_manager`.

Run the schema:

```bash
psql -U postgres -d smart_task_manager -f database/schema.sql
```

## Create Admin User

Use the helper script:

```bash
python create_admin.py
```

On this Windows system, if `python` is not recognized, use:

```bash
py create_admin.py
```

The script creates a new admin account. If the email already exists, it upgrades that user to admin.

You can also register a normal user from the website first, then change that user's role manually in PostgreSQL:

```sql
UPDATE users SET role = 'admin' WHERE email = 'your_email@example.com';
```

## Run Locally

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## API Endpoints

Authentication:

- `POST /register`
- `GET /verify-otp`
- `POST /verify-otp`
- `POST /login`
- `GET /logout`
- `GET /api/session`

Tasks:

- `GET /tasks`
- `POST /task/add`
- `PUT /task/update`
- `PUT /task/complete`
- `DELETE /task/delete`

Admin:

- `GET /admin`
- `GET /users`
- `GET /admin/tasks`
- `DELETE /user/delete`
- `DELETE /admin/task/delete`

## Deployment Notes

For Railway deployment, connect the GitHub repository, add the same environment variables from `.env.example`, connect a PostgreSQL database, and use this start command:

```bash
gunicorn app:app
```
