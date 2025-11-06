import os
from datetime import datetime, date
import tkinter as tk
from tkinter import messagebox, ttk

DATETIME_STRING_FORMAT = "%Y-%m-%d"

# ===== Helper Functions =====
def load_users():
    if not os.path.exists("user.txt"):
        with open("user.txt", "w") as f:
            f.write("admin;password")

    users = {}
    with open("user.txt", "r") as f:
        for line in f:
            if ";" in line:
                username, password = line.strip().split(";")
                users[username] = password
    return users

def load_tasks():
    if not os.path.exists("tasks.txt"):
        with open("tasks.txt", "w") as f:
            pass
    tasks = []
    with open("tasks.txt", "r") as f:
        for line in f:
            if not line.strip():
                continue
            username, title, description, due_date, assigned_date, completed = line.strip().split(";")
            task = {
                "username": username,
                "title": title,
                "description": description,
                "due_date": datetime.strptime(due_date, DATETIME_STRING_FORMAT).date(),
                "assigned_date": datetime.strptime(assigned_date, DATETIME_STRING_FORMAT).date(),
                "completed": True if completed == "Yes" else False,
            }
            tasks.append(task)
    return tasks

def save_tasks():
    with open("tasks.txt", "w") as f:
        for t in task_list:
            f.write(f"{t['username']};{t['title']};{t['description']};{t['due_date']};{t['assigned_date']};{'Yes' if t['completed'] else 'No'}\n")

# ===== GUI Functions =====
def login():
    username = entry_user.get()
    password = entry_pass.get()

    if username not in username_password or username_password[username] != password:
        messagebox.showerror("Login Failed", "Invalid username or password")
        return
    messagebox.showinfo("Login Success", f"Welcome {username}!")
    root.destroy()
    open_dashboard(username)

def open_dashboard(user):
    dashboard = tk.Tk()
    dashboard.title("Task Manager Dashboard")
    dashboard.geometry("700x500")

    tk.Label(dashboard, text=f"Logged in as: {user}", font=("Arial", 10), anchor="w").pack(pady=5)

    frame = tk.Frame(dashboard)
    frame.pack(pady=20)

    if user == "admin":
        tk.Button(frame, text="Register User", width=25, command=lambda: reg_user_window(user)).grid(row=0, column=0, pady=5)
        tk.Button(frame, text="Generate Reports", width=25, command=generate_reports).grid(row=1, column=0, pady=5)
        tk.Button(frame, text="Display Statistics", width=25, command=display_statistics).grid(row=2, column=0, pady=5)

    tk.Button(frame, text="Add Task", width=25, command=lambda: add_task_window(user)).grid(row=3, column=0, pady=5)
    tk.Button(frame, text="View All Tasks", width=25, command=view_all_tasks).grid(row=4, column=0, pady=5)
    tk.Button(frame, text="View My Tasks", width=25, command=lambda: view_my_tasks(user)).grid(row=5, column=0, pady=5)
    tk.Button(frame, text="Exit", width=25, command=dashboard.destroy).grid(row=6, column=0, pady=10)

    dashboard.mainloop()

def reg_user_window(current_user):
    win = tk.Toplevel()
    win.title("Register New User")
    win.geometry("350x250")

    tk.Label(win, text="Username:").pack()
    new_user = tk.Entry(win)
    new_user.pack()

    tk.Label(win, text="Password:").pack()
    new_pass = tk.Entry(win, show="*")
    new_pass.pack()

    tk.Label(win, text="Confirm Password:").pack()
    confirm_pass = tk.Entry(win, show="*")
    confirm_pass.pack()

    def save_user():
        if new_pass.get() != confirm_pass.get():
            messagebox.showerror("Error", "Passwords do not match")
            return
        if new_user.get() in username_password:
            messagebox.showerror("Error", "Username already exists")
            return

        with open("user.txt", "a") as f:
            f.write(f"\n{new_user.get()};{new_pass.get()}")
        username_password[new_user.get()] = new_pass.get()
        messagebox.showinfo("Success", "User registered successfully")
        win.destroy()

    tk.Button(win, text="Register", command=save_user).pack(pady=10)

def add_task_window(current_user):
    win = tk.Toplevel()
    win.title("Add Task")
    win.geometry("400x400")

    tk.Label(win, text="Assign to (username):").pack()
    entry_user_task = tk.Entry(win)
    entry_user_task.pack()

    tk.Label(win, text="Title:").pack()
    entry_title = tk.Entry(win)
    entry_title.pack()

    tk.Label(win, text="Description:").pack()
    entry_desc = tk.Entry(win)
    entry_desc.pack()

    tk.Label(win, text="Due Date (YYYY-MM-DD):").pack()
    entry_due = tk.Entry(win)
    entry_due.pack()

    def save_task():
        assigned_to = entry_user_task.get()
        if assigned_to not in username_password:
            messagebox.showerror("Error", "User does not exist")
            return
        try:
            due_date = datetime.strptime(entry_due.get(), DATETIME_STRING_FORMAT).date()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format")
            return
        if due_date < date.today():
            messagebox.showerror("Error", "Due date must be in the future")
            return
        task_list.append({
            "username": assigned_to,
            "title": entry_title.get(),
            "description": entry_desc.get(),
            "assigned_date": date.today(),
            "due_date": due_date,
            "completed": False
        })
        save_tasks()
        messagebox.showinfo("Success", "Task added successfully")
        win.destroy()

    tk.Button(win, text="Save Task", command=save_task).pack(pady=10)

def view_all_tasks():
    win = tk.Toplevel()
    win.title("All Tasks")
    win.geometry("600x400")

    tree = ttk.Treeview(win, columns=("User", "Title", "Due", "Status"), show="headings")
    tree.heading("User", text="User")
    tree.heading("Title", text="Title")
    tree.heading("Due", text="Due Date")
    tree.heading("Status", text="Completed")

    for t in task_list:
        tree.insert("", "end", values=(t["username"], t["title"], t["due_date"], "Yes" if t["completed"] else "No"))
    tree.pack(expand=True, fill="both")

def view_my_tasks(user):
    win = tk.Toplevel()
    win.title("My Tasks")
    win.geometry("600x400")

    user_tasks = [t for t in task_list if t["username"] == user]

    tree = ttk.Treeview(win, columns=("Title", "Due", "Status"), show="headings")
    tree.heading("Title", text="Title")
    tree.heading("Due", text="Due Date")
    tree.heading("Status", text="Completed")

    for t in user_tasks:
        tree.insert("", "end", values=(t["title"], t["due_date"], "Yes" if t["completed"] else "No"))
    tree.pack(expand=True, fill="both")

def generate_reports():
    total = len(task_list)
    completed = len([t for t in task_list if t["completed"]])
    incomplete = total - completed
    overdue = len([t for t in task_list if not t["completed"] and t["due_date"] < date.today()])

    with open("task_overview.txt", "w") as f:
        f.write(f"Total: {total}\nCompleted: {completed}\nIncomplete: {incomplete}\nOverdue: {overdue}\n")

    messagebox.showinfo("Report", "Reports generated successfully.")

def display_statistics():
    try:
        with open("task_overview.txt", "r") as f:
            stats = f.read()
        messagebox.showinfo("Statistics", stats)
    except FileNotFoundError:
        messagebox.showerror("Error", "No report found. Generate it first.")

# ===== Main Login Window =====
username_password = load_users()
task_list = load_tasks()

root = tk.Tk()
root.title("Task Manager Login")
root.geometry("350x250")

tk.Label(root, text="Username:").pack()
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Password:").pack()
entry_pass = tk.Entry(root, show="*")
entry_pass.pack()

tk.Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()
