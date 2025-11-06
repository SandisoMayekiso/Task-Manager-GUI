# Task Manager (Flask Web GUI)

A small Task Manager web app (Flask) for demoing on portfolio/GitHub. Uses simple text files for storage:
- `user.txt` — user;password per line
- `tasks.txt` — semicolon-separated task entries

## Features
- Login (default admin/admin: `admin;password`)
- Admin-only: Register user, generate reports, view stats
- Add task, view all tasks, view my tasks
- Generate simple text reports

## Install
1. `python -m venv venv`
2. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (macOS/Linux)
3. `pip install -r requirements.txt`

## Run
`python app.py`

Open http://127.0.0.1:5000

## Notes
- For production, set `TM_SECRET_KEY` env var to a secure value.
- Be careful exposing raw file download endpoints in public deployments.
- This is a demo app; not intended for production use.