from datetime import date, datetime


PRIORITY_POINTS = {"low": 10, "medium": 25, "high": 45, "critical": 65}


def parse_deadline(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def priority_score(task, today=None):
    """Return transparent heuristic score and explanation.

    Formula: priority base + importance*6 + deadline urgency + quick-win bonus.
    Completed tasks are ineligible. This is a prioritization aid, not a prediction.
    """
    today = today or date.today()
    if task["status"] == "completed":
        return 0, "Completed tasks are excluded from recommendations."

    deadline = parse_deadline(task["deadline"])
    days_left = (deadline - today).days
    score = PRIORITY_POINTS[task["priority"]] + int(task["importance"]) * 6
    reasons = []

    if days_left < 0:
        score += 80 + min(abs(days_left) * 3, 30)
        reasons.append("it is overdue")
    elif days_left == 0:
        score += 65
        reasons.append("it is due today")
    elif days_left == 1:
        score += 48
        reasons.append("it is due tomorrow")
    elif days_left <= 3:
        score += 30
        reasons.append(f"its deadline is in {days_left} days")
    elif days_left <= 7:
        score += 15
        reasons.append("its deadline is this week")

    if task["priority"] in {"high", "critical"}:
        reasons.append(f"it has {task['priority']} priority")
    if int(task["importance"]) >= 8:
        reasons.append("it has high importance")
    if int(task["estimated_minutes"]) <= 30:
        score += 12
        reasons.append(f"it needs only {task['estimated_minutes']} minutes")
    elif int(task["estimated_minutes"]) <= 60:
        score += 6
        reasons.append(f"it needs just {task['estimated_minutes']} minutes")

    if task["status"] == "in_progress":
        score += 8
        reasons.append("it is already in progress")

    explanation = "Recommended first because " + ", ".join(reasons[:3]) + "."
    return score, explanation


def recommend_next(tasks, today=None):
    candidates = []
    for task in tasks:
        if task["status"] != "completed":
            score, explanation = priority_score(task, today)
            candidates.append((score, task, explanation))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]["deadline"], -item[1]["importance"]), reverse=True)
    score, task, explanation = candidates[0]
    return {"task": task, "score": score, "explanation": explanation}
