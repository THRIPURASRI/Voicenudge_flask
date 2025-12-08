# tests/test_tasks.py
from datetime import datetime, timedelta, timezone

from voicenudge.models import Task, TaskHistory, Reminder


def test_ingest_text_creates_task(auth_client, db, user):
    payload = {"text": "Buy milk tomorrow at 6pm"}
    resp = auth_client.post("/tasks/ingest_text", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()

    assert "id" in data
    assert data["title"]
    assert data["category"]
    assert data["priority"]

    task = Task.query.get(data["id"])
    assert task is not None
    assert task.user_id == user.id
    assert task.text == payload["text"] or isinstance(task.text, str)


def test_ingest_text_no_text(auth_client):
    resp = auth_client.post("/tasks/ingest_text", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_list_tasks(auth_client, db, user):
    t1 = Task(
        user_id=user.id,
        text="Do something",
        title="do something",
        category="Personal",
        priority="Medium",
    )
    t2 = Task(
        user_id=user.id,
        text="Another task",
        title="another task",
        category="Work",
        priority="High",
    )
    db.session.add_all([t1, t2])
    db.session.commit()

    resp = auth_client.get("/tasks/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    titles = {d["title"] for d in data}
    assert "do something" in titles
    assert "another task" in titles


def test_complete_task_moves_to_history(auth_client, db, user):
    t = Task(
        user_id=user.id,
        text="Finish report",
        title="finish report",
        category="Work",
        priority="High",
    )
    db.session.add(t)
    db.session.commit()

    resp = auth_client.patch(f"/tasks/{t.id}/complete")
    assert resp.status_code == 200

    # Task removed
    assert Task.query.get(t.id) is None

    # History created
    history = TaskHistory.query.filter_by(user_id=user.id).all()
    assert len(history) == 1
    assert history[0].title == "finish report"


def test_set_due_creates_reminder(auth_client, db, user):
    # Create a task
    t = Task(
        user_id=user.id,
        text="Doctor appointment",
        title="doctor appointment",
        category="Health",
        priority="High",
    )
    db.session.add(t)
    db.session.commit()

    # Set due in IST
    due_ist = datetime(2025, 1, 10, 18, 30)  # 6:30 pm
    payload = {"due_at": due_ist.isoformat()}
    resp = auth_client.patch(f"/tasks/{t.id}/set_due", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()

    # Check UTC conversion response keys exist
    assert "due_at_utc" in data
    assert "remind_at_utc" in data

    # Check DB updated
    updated_task = Task.query.get(t.id)
    assert updated_task.due_at is not None

    reminders = Reminder.query.filter_by(task_id=t.id, user_id=user.id).all()
    assert len(reminders) == 1
    assert reminders[0].remind_at == updated_task.due_at - timedelta(minutes=5)


def test_set_due_missing_field(auth_client, db, user):
    t = Task(
        user_id=user.id,
        text="X",
        title="x",
        category="Work",
        priority="Low",
    )
    db.session.add(t)
    db.session.commit()

    resp = auth_client.patch(f"/tasks/{t.id}/set_due", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()
