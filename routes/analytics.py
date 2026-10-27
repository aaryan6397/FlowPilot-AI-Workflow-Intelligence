from datetime import date

from flask import Blueprint, render_template

from database.db import get_db

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/")
def analytics():
    tasks = get_db().execute("SELECT * FROM tasks ORDER BY created_at ASC").fetchall()
    total = len(tasks)
    status_counts = {status: sum(task["status"] == status for task in tasks) for status in ("todo", "in_progress", "completed")}
    priority_counts = {priority: sum(task["priority"] == priority for task in tasks) for priority in ("low", "medium", "high", "critical")}
    categories = {}
    for task in tasks:
        categories[task["category"]] = categories.get(task["category"], 0) + int(task["estimated_minutes"])
    today = date.today()
    remaining_effort = sum(int(task["estimated_minutes"]) for task in tasks if task["status"] != "completed")
    overdue = sum(task["status"] != "completed" and date.fromisoformat(task["deadline"]) < today for task in tasks)
    return render_template("analytics.html", total=total, status_counts=status_counts, priority_counts=priority_counts, categories=categories, remaining_effort=remaining_effort, overdue=overdue)
