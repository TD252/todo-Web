import os
import sqlite3
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-taskforge-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "taskforge.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite database and create the tasks table if needed."""
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            notes TEXT,
            priority TEXT DEFAULT 'Medium',
            deadline DATE,
            is_complete INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


# Initialize the database at startup so taskforge.db exists before the first request.
init_db()


def parse_deadline(deadline_str):
    if not deadline_str:
        return None
    try:
        return datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def build_task_payload(task):
    today = date.today()
    deadline = parse_deadline(task["deadline"])
    days_remaining = None
    is_overdue = False

    if deadline:
        days_remaining = (deadline - today).days
        is_overdue = days_remaining < 0 and task["is_complete"] == 0

    return {
        "id": task["id"],
        "title": task["title"],
        "notes": task["notes"],
        "priority": task["priority"],
        "deadline": task["deadline"],
        "is_complete": task["is_complete"],
        "created_at": task["created_at"],
        "days_remaining": days_remaining,
        "is_overdue": is_overdue,
    }


@app.route("/")
def index():
    filter_value = request.args.get("filter", "all")
    sort_value = request.args.get("sort", "created")

    query = "SELECT * FROM tasks"
    conditions = []
    params = []

    if filter_value == "active":
        conditions.append("is_complete = 0")
    elif filter_value == "completed":
        conditions.append("is_complete = 1")
    elif filter_value == "overdue":
        conditions.append("is_complete = 0")
        conditions.append("deadline IS NOT NULL")
        conditions.append("deadline < date('now')")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if sort_value == "priority":
        query += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 ELSE 4 END, deadline IS NULL, deadline ASC"
    elif sort_value == "deadline":
        query += " ORDER BY deadline IS NULL, deadline ASC"
    else:
        query += " ORDER BY created_at DESC"

    conn = get_db_connection()
    tasks = [build_task_payload(row) for row in conn.execute(query, params).fetchall()]
    conn.close()

    return render_template(
        "index.html",
        tasks=tasks,
        current_filter=filter_value,
        current_sort=sort_value,
    )


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "Medium")
    deadline = request.form.get("deadline") or None
    notes = request.form.get("notes", "").strip()

    if not title:
        flash("A task title is required.")
        return redirect(url_for("index"))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (title, notes, priority, deadline) VALUES (?, ?, ?, ?)",
        (title, notes, priority, deadline),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    conn = get_db_connection()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()

    if task is None:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        priority = request.form.get("priority", "Medium")
        deadline = request.form.get("deadline") or None
        notes = request.form.get("notes", "").strip()

        if not title:
            flash("A task title is required.")
            return redirect(url_for("edit_task", task_id=task_id))

        conn = get_db_connection()
        conn.execute(
            "UPDATE tasks SET title = ?, notes = ?, priority = ?, deadline = ? WHERE id = ?",
            (title, notes, priority, deadline, task_id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("edit.html", task=task)


@app.route("/complete/<int:task_id>", methods=["POST"])
def toggle_complete(task_id):
    conn = get_db_connection()
    task = conn.execute("SELECT is_complete FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        abort(404)

    new_status = 0 if task["is_complete"] == 1 else 1
    conn.execute("UPDATE tasks SET is_complete = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
