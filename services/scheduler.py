from datetime import date, datetime


def reschedule_advice(task, other_tasks, proposed_deadline):
    proposed = datetime.strptime(proposed_deadline, "%Y-%m-%d").date()
    today = date.today()
    conflicts = [
        other for other in other_tasks
        if other["id"] != task["id"]
        and other["status"] != "completed"
        and abs((datetime.strptime(other["deadline"], "%Y-%m-%d").date() - proposed).days) <= 1
    ]
    notes = []
    if proposed < today:
        notes.append("The selected date is in the past, so choose today or a future date.")
    if conflicts:
        notes.append(f"{len(conflicts)} active task(s) are scheduled within one day of this deadline.")
    if not notes:
        notes.append("No near-deadline conflict was found. Confirm to apply this new plan.")
    return {"is_valid": proposed >= today, "conflicts": conflicts, "message": " ".join(notes)}
