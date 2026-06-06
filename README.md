# TaskForge

TaskForge is a Python Flask to-do web app built for tracking tasks with priority levels, deadline countdowns, and smart filters. It uses SQLite for lightweight persistence and Jinja2 templates for a polished dark-mode interface.

## Features

- Create tasks with title, notes, priority, and deadline
- Filter tasks by All, Active, Completed, and Overdue
- Sort tasks by priority, deadline, or creation date
- Mark tasks complete and delete tasks with one click
- Deadline countdown and overdue highlighting
- Dark mode UI with clean cards and color-coded priority badges

## Tech Stack

- Python
- Flask
- SQLite
- Jinja2
- HTML/CSS

## Setup in GitHub Codespaces

1. Open the repository in GitHub Codespaces.
2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install Flask:

```bash
pip install flask
```

4. Run the app:

```bash
python app.py
```

5. Open the displayed URL in your browser, usually `http://0.0.0.0:5000`.

## How to Use TaskForge

- Add a new task using the form on the home page.
- Use filter tabs to view only active, completed, or overdue tasks.
- Sort your task list by newest created, nearest deadline, or priority.
- Click the checkmark button to toggle completion and the trash button to delete a task.
- Edit a task by clicking its Edit button.

## Project Structure

```
/taskforge
│
├── app.py
├── taskforge.db          # created automatically when the app runs
├── README.md
├── static/
│   └── style.css
└── templates/
    ├── edit.html
    └── index.html
```

## Database

The app initializes a SQLite database with a `tasks` table containing:

- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `title` TEXT NOT NULL
- `notes` TEXT
- `priority` TEXT DEFAULT 'Medium'
- `deadline` DATE
- `is_complete` INTEGER DEFAULT 0
- `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
