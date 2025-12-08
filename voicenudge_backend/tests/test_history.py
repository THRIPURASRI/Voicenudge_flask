# tests/test_history.py

from voicenudge.models import Task, TaskHistory


def test_list_history_returns_completed_and_archived(auth_client, db, user):
    """
    Tests GET /history/:
    - Completed tasks still inside Task table (status='completed')
    - Archived tasks inside TaskHistory table
    """

    # ---------------------------
    # 1. Create completed task
    # ---------------------------
    completed_task = Task(
        user_id=user.id,
        text="Finish assignment",
        title="finish assignment",
        category="Work",
        priority="High",
        status="completed",
    )
    db.session.add(completed_task)
    db.session.commit()

    # ---------------------------
    # 2. Create archived task (TaskHistory)
    # ---------------------------
    archived_task = TaskHistory(
        user_id=user.id,
        task_id=completed_task.id,
        text="Finish assignment (old)",
        title="finish assignment (old)",
        category="Work",
        priority="Medium",
    )
    db.session.add(archived_task)
    db.session.commit()

    # ---------------------------
    # 3. Call /history/
    # ---------------------------
    resp = auth_client.get("/history/")
    assert resp.status_code == 200

    data = resp.get_json()
    assert isinstance(data, list)

    # Should contain 2 entries (1 completed + 1 archived)
    assert len(data) == 2

    sources = {d["source"] for d in data}
    assert "tasks" in sources
    assert "history" in sources

    # Ensure fields exist
    for item in data:
        assert "title" in item
        assert "category" in item
        assert "priority" in item
        assert "status" in item


def test_clear_history_deletes_only_archived(auth_client, db, user):
    """
    Tests DELETE /history/clear:
    - Should delete ONLY TaskHistory rows
    - Should NOT delete completed tasks stored in Task table
    """

    # Create completed task (still inside tasks table)
    completed_task = Task(
        user_id=user.id,
        text="Buy groceries",
        title="buy groceries",
        category="Errands",
        priority="Medium",
        status="completed",
    )
    db.session.add(completed_task)
    db.session.commit()

    # Create archived history entry
    archived_entry = TaskHistory(
        user_id=user.id,
        task_id=completed_task.id,
        text="Buy groceries (old)",
        title="buy groceries (old)",
        category="Errands",
        priority="Low",
    )
    db.session.add(archived_entry)
    db.session.commit()

    # Confirm history exists
    assert TaskHistory.query.filter_by(user_id=user.id).count() == 1

    # Call DELETE /history/clear
    resp = auth_client.delete("/history/clear")
    assert resp.status_code == 200

    data = resp.get_json()
    assert "message" in data

    # Archived history must now be empty
    assert TaskHistory.query.filter_by(user_id=user.id).count() == 0

    # Completed task must STILL exist in tasks table
    remaining_task = Task.query.filter_by(user_id=user.id).first()
    assert remaining_task is not None
    assert remaining_task.status == "completed"
