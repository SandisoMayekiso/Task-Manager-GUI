import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename

# --- Config ---
DATETIME_STRING_FORMAT = "%Y-%m-%d"
SECRET_KEY = os.environ.get("TM_SECRET_KEY", "change_this_to_a_secure_key")

app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- Data storage helpers (text files) ---
USER_FILE = "user.txt"
TASK_FILE = "tasks.txt"
TASK_OVERVIEW = "task_overview.txt"
USER_OVERVIEW = "user_overview.txt"

def ensure_files():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            f.write("admin;password")
    if not os.path.exists(TASK_FILE):
        with open(TASK_FILE, "w") as f:
            pass

def load_users():
    ensure_files()
    users = {}
    with open(USER_FILE, "r") as f:
        for line in f:
            if ";" in line:
                username, passwd = line.strip().split(";", 1)
                users[username.strip()] = passwd.strip()
    return users

def save_user(username, password):
    with open(USER_FILE, "a") as f:
        f.write(f"\n{username};{password}")

def load_tasks():
    ensure_files()
    tasks = []
    with open(TASK_FILE, "r") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split(";")
            if len(parts) != 6:
                continue
            username, title, description, due_date_str, assigned_date_str, completed_str = parts
            try:
                due_date = datetime.strptime(due_date_str, DATETIME_STRING_FORMAT).date()
                assigned_date = datetime.strptime(assigned_date_str, DATETIME_STRING_FORMAT).date()
            except Exception:
                continue
            tasks.append({
                "username": username,
                "title": title,
                "description": description,
                "due_date": due_date,
                "assigned_date": assigned_date,
                "completed": True if completed_str == "Yes" else False
            })
    return tasks

def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        for t in tasks:
            f.write(f"{t['username']};{t['title']};{t['description']};{t['due_date'].strftime(DATETIME_STRING_FORMAT)};{t['assigned_date'].strftime(DATETIME_STRING_FORMAT)};{'Yes' if t['completed'] else 'No'}\n")

# --- Auth helpers ---
def is_logged_in():
    return "username" in session

def is_admin():
    return session.get("username") == "admin"

# --- Routes ---
@app.route("/")
def index():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username in users and users[username] == password:
            session["username"] = username
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))
    tasks = load_tasks()
    user = session["username"]
    # summary counts for display
    total = len(tasks)
    completed = len([t for t in tasks if t["completed"]])
    overdue = len([t for t in tasks if not t["completed"] and t["due_date"] < date.today()])
    return render_template("dashboard.html", user=user, total=total, completed=completed, overdue=overdue, admin=is_admin())

@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if not is_logged_in():
        return redirect(url_for("login"))
    users = load_users()
    if request.method == "POST":
        assigned_to = request.form.get("assigned_to", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        due_date_str = request.form.get("due_date", "").strip()
        if assigned_to not in users:
            flash("Assigned user does not exist.", "danger")
            return redirect(url_for("add_task"))
        try:
            due_date = datetime.strptime(due_date_str, DATETIME_STRING_FORMAT).date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for("add_task"))
        if due_date < date.today():
            flash("Due date must be in the future.", "danger")
            return redirect(url_for("add_task"))
        tasks = load_tasks()
        tasks.append({
            "username": assigned_to,
            "title": title,
            "description": description,
            "due_date": due_date,
            "assigned_date": date.today(),
            "completed": False
        })
        save_tasks(tasks)
        flash("Task added successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_task.html", users=load_users().keys())

@app.route("/view_all")
def view_all():
    if not is_logged_in():
        return redirect(url_for("login"))
    tasks = load_tasks()
    return render_template("view_all.html", tasks=tasks)

@app.route("/view_mine")
def view_mine():
    if not is_logged_in():
        return redirect(url_for("login"))
    user = session["username"]
    tasks = [t for t in load_tasks() if t["username"] == user]
    return render_template("view_mine.html", tasks=tasks)

@app.route("/register", methods=["GET", "POST"])
def register():
    if not is_logged_in() or not is_admin():
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        new_password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()
        users = load_users()
        if new_username in users:
            flash("Username already exists.", "danger")
            return redirect(url_for("register"))
        if new_password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))
        save_user(new_username, new_password)
        flash("User registered.", "success")
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/generate_reports")
def generate_reports():
    if not is_logged_in() or not is_admin():
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))
    tasks = load_tasks()
    total = len(tasks)
    completed = len([t for t in tasks if t["completed"]])
    incomplete = total - completed
    overdue = len([t for t in tasks if not t["completed"] and t["due_date"] < date.today()])

    with open(TASK_OVERVIEW, "w") as f:
        f.write(f"Total tasks: {total}\nCompleted: {completed}\nIncomplete: {incomplete}\nOverdue: {overdue}\n")

    with open(USER_OVERVIEW, "w") as f:
        users = load_users()
        for user in users.keys():
            user_tasks = [t for t in tasks if t["username"] == user]
            if user_tasks:
                comp = len([t for t in user_tasks if t["completed"]])
                inc = len([t for t in user_tasks if not t["completed"]])
                ovd = len([t for t in user_tasks if not t["completed"] and t["due_date"] < date.today()])
                f.write(f"{user} - Total: {len(user_tasks)}, Completed: {comp}, Incomplete: {inc}, Overdue: {ovd}\n")
            else:
                f.write(f"{user} - No tasks assigned.\n")

    flash("Reports generated.", "success")
    return redirect(url_for("dashboard"))

@app.route("/stats")
def stats():
    if not is_logged_in() or not is_admin():
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))
    try:
        with open(TASK_OVERVIEW, "r") as f:
            task_text = f.read()
    except FileNotFoundError:
        task_text = None
    try:
        with open(USER_OVERVIEW, "r") as f:
            user_text = f.read()
    except FileNotFoundError:
        user_text = None
    return render_template("stats.html", task_text=task_text, user_text=user_text)

# Serve files if needed (e.g., to download reports)
@app.route("/files/<path:filename>")
def download_file(filename):
    return send_from_directory(".", filename, as_attachment=True)

# --- Start ---
if __name__ == "__main__":
    ensure_files()
    app.run(debug=True)
