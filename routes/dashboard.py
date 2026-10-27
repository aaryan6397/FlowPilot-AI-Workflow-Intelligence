from datetime import date, timedelta

from flask import Blueprint, render_template

from database.db import get_db
from services.priority_engine import priority_score, recommend_next

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    database = get_db()
    tasks = database.execute("SELECT * FROM tasks ORDER BY deadline ASC").fetchall()
    today = date.today()
    incomplete = [task for task in tasks if task["status"] != "completed"]
    overdue = [task for task in incomplete if date.fromisoformat(task["deadline"]) < today]
    upcoming = [task for task in incomplete if today <= date.fromisoformat(task["deadline"]) <= today + timedelta(days=7)]
    completed = [task for task in tasks if task["status"] == "completed"]
    total = len(tasks)
    recommendation = recommend_next(incomplete, today)
    ranked = []
    for task in incomplete:
        score, explanation = priority_score(task, today)
        ranked.append({"task": task, "score": score, "explanation": explanation})
    ranked.sort(key=lambda item: item["score"], reverse=True)
    metrics = {
        "total": total,
        "in_progress": sum(task["status"] == "in_progress" for task in tasks),
        "completed": len(completed),
        "overdue": len(overdue),
        "completion_rate": round((len(completed) / total) * 100) if total else 0,
        "upcoming": len(upcoming),
    }
    return render_template("dashboard.html", metrics=metrics, recommendation=recommendation, ranked=ranked[:5], overdue=overdue[:4], today=today)
