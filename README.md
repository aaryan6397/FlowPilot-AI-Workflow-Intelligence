# FlowPilot - AI Workflow Intelligence

> **Plan Smarter. Prioritize Better. Achieve More.**

FlowPilot is a polished local-first task-management prototype for people who need help deciding what to work on next. It combines task CRUD, deadline-aware planning, transparent rule-based recommendations, rescheduling checks and real-data workflow insights.

## Problem

When tasks, deadlines and priorities change, people often manually reorganize work and lose clarity about the next best action. Generic task lists show *what* exists but do not clearly explain *what should happen next*.

## Solution

FlowPilot turns saved task data into a clear workflow dashboard. The priority engine uses deadline urgency, priority, importance, estimated effort and status to rank active tasks. Each recommendation includes a readable reason. It is **rule-based logic, not an LLM or an AI prediction**.

## Implemented features

- Complete task CRUD: title, description, category, priority, status, deadline, estimated effort and importance.
- Dashboard metrics calculated from SQLite records: total, in-progress, completed, overdue, completion rate and upcoming work.
- “What should I do next?” card using documented transparent scoring.
- Priority radar with score and explanation for active tasks.
- Completion / reopen workflow with completion timestamp.
- Adaptive rescheduling with future-date validation, conflict warning and explicit confirmation.
- Search, combined filters and sorting by deadline, priority or creation date.
- Analytics for task status, priority distribution, workload by category and remaining effort.
- Responsive modern dashboard UI with accessible focus states and mobile sidebar.
- CSRF protection for state-changing forms, parameterized SQLite queries, server-side validation and custom error pages.
- Optional, non-duplicating fictional demo-data script.
- Automated Pytest coverage for core workflows.

## Screenshots

Screenshots are intentionally not included in this repository.


## Priority formula

```
score = priority base + (importance × 6) + deadline urgency + quick-win bonus
```

- Overdue tasks receive the largest urgency boost.
- Today/tomorrow/this-week deadlines receive decreasing urgency boosts.
- High and critical priority, high importance and short estimated effort raise the score.
- Completed tasks are excluded.

The score is an understandable decision aid; it is not presented as an objectively accurate prediction.

## Tech stack

- Python 3, Flask and Jinja2
- SQLite using Python’s parameterized `sqlite3` library
- HTML5, CSS3 and vanilla JavaScript
- Pytest
- Git

## Project structure

```
flowpilot/
├── app.py
├── config.py
├── database/          # SQLite connection and schema
├── routes/            # Dashboard, task and analytics routes
├── services/          # Priority engine and scheduler rules
├── templates/         # Jinja UI templates
├── static/            # CSS and JavaScript
├── scripts/           # Optional demo data
└── tests/             # Automated tests
```

## Local setup (Windows PowerShell)

```powershell
cd "C:\Users\aryan\OneDrive\Desktop\HACKATHON PROJECTS\FLOWPILOT AI WORKFLOW INTELLIGENCE"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open http://127.0.0.1:5000.

The database file and table are created automatically at `instance/flowpilot.db`.

## Demo data

```powershell
python scripts\seed_demo.py
```

This creates five clearly fictional records with `is_demo=1`. Running it again does not duplicate them. For a full local reset, stop the app and delete only `instance/flowpilot.db`; it contains all locally stored tasks.

## Tests

```powershell
pytest -q
```

## Known limitations

- This is a local single-user prototype; it intentionally has no fake login system or external integrations.
- SQLite is ideal for development and demos; PostgreSQL would be preferable for concurrent production deployment.
- Scheduling checks compare nearby deadlines but do not yet include calendars, working hours or recurring tasks.
- The scoring engine is deterministic and is not a trained AI model.

## Future roadmap

- Optional real authentication and per-user workspaces.
- Calendar export/import and time-block scheduling.
- Configurable scoring weights and SLA-like goal policies.
- PostgreSQL deployment, cloud backups and monitoring.
- Opt-in LLM integration for natural-language planning only after a genuine provider is configured.

## Devpost short description

FlowPilot helps students and makers escape task-list overload. Instead of showing a static list, it calculates a transparent priority score from deadlines, importance, effort and task state, then explains the best next action. Users can adjust plans through confirmed rescheduling and monitor their workflow with live analytics.

## 3-minute demo outline

1. **0:00-0:25:** Explain the problem: people know their tasks but not the next best action.
2. **0:25-0:55:** Create a high-importance task with deadline and effort.
3. **0:55-1:25:** Show dashboard metrics and the explained next-task recommendation.
4. **1:25-1:50:** Mark a task complete and show metrics update.
5. **1:50-2:20:** Open an overdue task, reschedule it, view conflict check, and explicitly confirm the new plan.
6. **2:20-2:45:** Show filters and the analytics page.
7. **2:45-3:00:** Explain transparent rule-based intelligence and future integrations.
