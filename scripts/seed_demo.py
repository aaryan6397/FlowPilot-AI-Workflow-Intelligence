"""Insert non-duplicated fictional data for a local hackathon demonstration."""
from datetime import date, timedelta, datetime, timezone
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app import create_app
from database.db import get_db


DEMO_TASKS = [
    ("Finalize FlowPilot demo script", "Write a clear three-minute walkthrough for judges.", "Hackathon", "critical", "in_progress", 1, 35, 9),
    ("Review dashboard accessibility", "Check contrast, keyboard focus and mobile navigation.", "Product", "high", "todo", 3, 45, 8),
    ("Prepare project README", "Document installation, features and rule-based scoring.", "Documentation", "high", "todo", 4, 60, 8),
    ("Organize research notes", "Move workflow observations into a concise outline.", "Research", "medium", "todo", 7, 45, 6),
    ("Update pitch slide", "Add the problem-to-solution story.", "Presentation", "low", "completed", -2, 25, 4),
]


def seed():
    app = create_app()
    with app.app_context():
        database = get_db()
        existing = database.execute("SELECT COUNT(*) AS count FROM tasks WHERE is_demo=1").fetchone()["count"]
        if existing:
            print("Demo data already exists. No duplicate tasks were inserted.")
            return
        for title, description, category, priority, status, days, effort, importance in DEMO_TASKS:
            completed_at = datetime.now(timezone.utc).isoformat(timespec="seconds") if status == "completed" else None
            database.execute("""INSERT INTO tasks (title, description, category, priority, status, deadline, estimated_minutes, importance, is_demo, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""", (title, description, category, priority, status, (date.today() + timedelta(days=days)).isoformat(), effort, importance, datetime.now(timezone.utc).isoformat(timespec="seconds"), completed_at))
        database.commit()
        print("Inserted 5 fictional demo tasks. They are marked is_demo=1.")


if __name__ == "__main__":
    seed()
