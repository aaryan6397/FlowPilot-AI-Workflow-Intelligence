from datetime import date, datetime, timezone
from functools import wraps
from secrets import token_urlsafe

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from database.db import get_db
from services.priority_engine import priority_score
from services.scheduler import reschedule_advice

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_STATUSES = {"todo", "in_progress", "completed"}


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = token_urlsafe(32)
    return session["csrf_token"]


def csrf_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if request.method == "GET":
            return view(*args, **kwargs)
        if request.form.get("csrf_token") != session.get("csrf_token"):
            abort(400, "Your form expired. Refresh the page and try again.")
        return view(*args, **kwargs)
    return wrapped


def task_or_404(task_id):
    task = get_db().execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        abort(404)
    return task


def validate_task(form):
    values = {
        "title": form.get("title", "").strip(),
        "description": form.get("description", "").strip(),
        "category": form.get("category", "").strip(),
        "priority": form.get("priority", "medium"),
        "status": form.get("status", "todo"),
        "deadline": form.get("deadline", ""),
        "estimated_minutes": form.get("estimated_minutes", ""),
        "importance": form.get("importance", ""),
    }
    errors = []
    if not 3 <= len(values["title"]) <= 120:
        errors.append("Title must be between 3 and 120 characters.")
    if len(values["description"]) > 2000:
        errors.append("Description cannot exceed 2,000 characters.")
    if not 2 <= len(values["category"]) <= 50:
        errors.append("Category must be between 2 and 50 characters.")
    if values["priority"] not in VALID_PRIORITIES:
        errors.append("Select a valid priority.")
    if values["status"] not in VALID_STATUSES:
        errors.append("Select a valid status.")
    try:
        deadline = datetime.strptime(values["deadline"], "%Y-%m-%d").date()
        if deadline.year > date.today().year + 10:
            errors.append("Deadline is too far in the future.")
    except ValueError:
        errors.append("Enter a valid deadline.")
    try:
        values["estimated_minutes"] = int(values["estimated_minutes"])
        if not 5 <= values["estimated_minutes"] <= 2400:
            errors.append("Estimated effort must be between 5 and 2,400 minutes.")
    except ValueError:
        errors.append("Estimated effort must be a whole number of minutes.")
    try:
        values["importance"] = int(values["importance"])
        if not 1 <= values["importance"] <= 10:
            errors.append("Importance must be between 1 and 10.")
    except ValueError:
        errors.append("Importance must be a number from 1 to 10.")
    return values, errors


@tasks_bp.route("/")
def index():
    filters = {key: request.args.get(key, "").strip() for key in ("q", "status", "priority", "category", "sort")}
    clauses, values = [], []
    if filters["q"]:
        clauses.append("LOWER(title) LIKE ?")
        values.append(f"%{filters['q'].lower()}%")
    for field in ("status", "priority", "category"):
        if filters[field]:
            clauses.append(f"{field} = ?")
            values.append(filters[field])
    order_map = {"deadline": "deadline ASC", "priority": "CASE priority WHEN 'critical' THEN 4 WHEN 'high' THEN 3 WHEN 'medium' THEN 2 ELSE 1 END DESC, deadline ASC", "created": "created_at DESC"}
    query = "SELECT * FROM tasks"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY " + order_map.get(filters["sort"], "deadline ASC")
    database = get_db()
    tasks = database.execute(query, values).fetchall()
    categories = database.execute("SELECT DISTINCT category FROM tasks ORDER BY category").fetchall()
    enriched = [{"task": task, "score": priority_score(task)[0] if task["status"] != "completed" else 0} for task in tasks]
    return render_template("tasks.html", tasks=enriched, categories=categories, filters=filters, today=date.today())


@tasks_bp.route("/new", methods=["GET", "POST"])
@csrf_required
def create():
    if request.method == "POST":
        values, errors = validate_task(request.form)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("task_form.html", task=values, mode="Create")
        completed_at = datetime.now(timezone.utc).isoformat(timespec="seconds") if values["status"] == "completed" else None
        database = get_db()
        database.execute("""INSERT INTO tasks (title, description, category, priority, status, deadline, estimated_minutes, importance, created_at, completed_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (*values.values(), datetime.now(timezone.utc).isoformat(timespec="seconds"), completed_at))
        database.commit()
        flash("Task created. Your dashboard metrics updated.", "success")
        return redirect(url_for("tasks.index"))
    return render_template("task_form.html", task={"priority":"medium", "status":"todo", "importance":5, "estimated_minutes":30, "deadline":date.today().isoformat()}, mode="Create")


@tasks_bp.route("/<int:task_id>")
def detail(task_id):
    task = task_or_404(task_id)
    score, explanation = priority_score(task)
    return render_template("task_detail.html", task=task, score=score, explanation=explanation, today=date.today())


@tasks_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
@csrf_required
def edit(task_id):
    task = task_or_404(task_id)
    if request.method == "POST":
        values, errors = validate_task(request.form)
        if errors:
            for error in errors:
                flash(error, "error")
            values["id"] = task_id
            return render_template("task_form.html", task=values, mode="Edit")
        completed_at = task["completed_at"]
        if values["status"] == "completed" and not completed_at:
            completed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if values["status"] != "completed":
            completed_at = None
        database = get_db()
        database.execute("""UPDATE tasks SET title=?, description=?, category=?, priority=?, status=?, deadline=?, estimated_minutes=?, importance=?, completed_at=? WHERE id=?""", (*values.values(), completed_at, task_id))
        database.commit()
        flash("Task updated successfully.", "success")
        return redirect(url_for("tasks.detail", task_id=task_id))
    return render_template("task_form.html", task=task, mode="Edit")


@tasks_bp.post("/<int:task_id>/toggle-complete")
@csrf_required
def toggle_complete(task_id):
    task = task_or_404(task_id)
    status = "todo" if task["status"] == "completed" else "completed"
    completed_at = None if status == "todo" else datetime.now(timezone.utc).isoformat(timespec="seconds")
    database = get_db()
    database.execute("UPDATE tasks SET status=?, completed_at=? WHERE id=?", (status, completed_at, task_id))
    database.commit()
    flash("Task reopened." if status == "todo" else "Great work - task marked complete!", "success")
    return redirect(request.referrer or url_for("tasks.index"))


@tasks_bp.post("/<int:task_id>/delete")
@csrf_required
def delete(task_id):
    task_or_404(task_id)
    database = get_db()
    database.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    database.commit()
    flash("Task deleted permanently.", "success")
    return redirect(url_for("tasks.index"))


@tasks_bp.route("/<int:task_id>/reschedule", methods=["GET", "POST"])
@csrf_required
def reschedule(task_id):
    task = task_or_404(task_id)
    database = get_db()
    if request.method == "POST":
        proposed = request.form.get("deadline", "")
        try:
            advice = reschedule_advice(task, database.execute("SELECT * FROM tasks").fetchall(), proposed)
        except ValueError:
            flash("Select a valid new deadline.", "error")
            return render_template("task_detail.html", task=task, score=priority_score(task)[0], explanation="", today=date.today(), reschedule_open=True)
        if not advice["is_valid"]:
            flash(advice["message"], "error")
            return render_template("task_detail.html", task=task, score=priority_score(task)[0], explanation="", today=date.today(), reschedule_open=True)
        if request.form.get("confirm") != "yes":
            return render_template("task_detail.html", task=task, score=priority_score(task)[0], explanation="", today=date.today(), reschedule_advice=advice, proposed_deadline=proposed)
        database.execute("UPDATE tasks SET deadline=? WHERE id=?", (proposed, task_id))
        database.commit()
        flash("New deadline confirmed and applied.", "success")
        return redirect(url_for("tasks.detail", task_id=task_id))
    return render_template("task_detail.html", task=task, score=priority_score(task)[0], explanation=priority_score(task)[1], today=date.today(), reschedule_open=True)
