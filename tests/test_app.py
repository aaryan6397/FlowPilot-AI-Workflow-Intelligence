import os
import tempfile
from datetime import date, timedelta

import pytest

from app import create_app
from database.db import get_db


@pytest.fixture()
def app():
    handle, path = tempfile.mkstemp()
    os.close(handle)
    app = create_app({"TESTING": True, "DATABASE_PATH": path, "SECRET_KEY": "test-secret"})
    yield app
    os.unlink(path)


@pytest.fixture()
def client(app):
    return app.test_client()


def csrf(client):
    client.get("/tasks/new")
    with client.session_transaction() as session:
        return session["csrf_token"]


def create_task(client, **changes):
    payload = {
        "title": "Finish prototype", "description": "A valid task", "category": "Hackathon",
        "priority": "high", "status": "todo", "deadline": (date.today() + timedelta(days=1)).isoformat(),
        "estimated_minutes": "30", "importance": "9", "csrf_token": csrf(client),
    }
    payload.update(changes)
    return client.post("/tasks/new", data=payload, follow_redirects=True)


def test_application_starts_and_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Make the next" in response.data


def test_task_creation_and_persistence(client, app):
    response = create_task(client)
    assert b"Task created" in response.data
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) AS count FROM tasks").fetchone()["count"] == 1


def test_invalid_task_is_rejected(client):
    response = create_task(client, title="x", estimated_minutes="0")
    assert b"Title must be" in response.data
    assert b"Estimated effort must" in response.data


def test_edit_completion_and_delete(client, app):
    create_task(client)
    with app.app_context():
        task_id = get_db().execute("SELECT id FROM tasks").fetchone()["id"]
    token = csrf(client)
    response = client.post(f"/tasks/{task_id}/toggle-complete", data={"csrf_token": token}, follow_redirects=True)
    assert b"marked complete" in response.data
    with app.app_context():
        assert get_db().execute("SELECT status FROM tasks WHERE id=?", (task_id,)).fetchone()["status"] == "completed"
    token = csrf(client)
    response = client.post(f"/tasks/{task_id}/delete", data={"csrf_token": token}, follow_redirects=True)
    assert b"Task deleted" in response.data


def test_recommendation_prioritizes_overdue_work(client):
    create_task(client, title="Future task", priority="low", deadline=(date.today()+timedelta(days=7)).isoformat(), importance="2")
    create_task(client, title="Overdue task", priority="medium", deadline=(date.today()-timedelta(days=1)).isoformat(), importance="5")
    response = client.get("/")
    assert b"Overdue task" in response.data
    assert b"Recommended first because it is overdue" in response.data


def test_reschedule_rejects_past_date(client, app):
    create_task(client)
    with app.app_context():
        task_id = get_db().execute("SELECT id FROM tasks").fetchone()["id"]
    response = client.post(f"/tasks/{task_id}/reschedule", data={"csrf_token": csrf(client), "deadline": (date.today()-timedelta(days=1)).isoformat()}, follow_redirects=True)
    assert b"selected date is in the past" in response.data


def test_analytics_supports_empty_database(client):
    response = client.get("/analytics/")
    assert response.status_code == 200
    assert b"Analytics will appear here" in response.data
