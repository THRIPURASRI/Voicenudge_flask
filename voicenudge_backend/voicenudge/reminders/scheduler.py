import logging
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

from flask_apscheduler import APScheduler
from flask_mail import Message

from voicenudge.extensions import db, mail
from voicenudge.models import Reminder, Task, TaskHistory, User

# Silence chatty APScheduler INFO messages in dev
logging.getLogger("apscheduler").setLevel(logging.WARNING)

scheduler = APScheduler()


def send_email(app, to, subject, body, html=None):
    """Send email via Flask-Mail, with robust logging."""
    try:
        sender = app.config.get("MAIL_DEFAULT_SENDER")  # use your .env default
        msg = Message(subject=subject, sender=sender, recipients=[to], body=body)
        if html:
            msg.html = html
        mail.send(msg)
        print(f"✅ Sent email to {to} • subject='{subject}'")
        return True
    except Exception as e:
        print(f"❌ Email send failed to {to}: {e}")
        return False


def _format_gcal_datetime(dt):
    """Convert timezone-aware datetime to Google Calendar UTC format."""
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.strftime("%Y%m%dT%H%M%SZ")


def build_calendar_link(task):
    """Generate 'Add to Google Calendar' link for the given task."""
    if not task.due_at:
        return None

    start = task.due_at
    end = task.due_at + timedelta(minutes=30)  # assume 30-minute event

    params = {
        "action": "TEMPLATE",
        "text": task.title or "Task Reminder",
        "dates": f"{_format_gcal_datetime(start)}/{_format_gcal_datetime(end)}",
        "details": f"Task: {task.title or ''}\n\n{task.text or ''}",
    }

    return "https://www.google.com/calendar/render?" + urlencode(params)


def check_reminders(app):
    """Check for due reminders and send emails."""
    with app.app_context():
        # Use timezone-aware UTC for consistency
        now = datetime.now(timezone.utc)
        print(f"⏰ Checking reminders at {now.isoformat()}")

        due_reminders = Reminder.query.filter(
            Reminder.remind_at <= now,
            Reminder.sent.is_(False),
        ).all()

        print(f"📋 Found {len(due_reminders)} due reminder(s)")

        for r in due_reminders:
            task = Task.query.get(r.task_id)
            user = User.query.get(r.user_id)

            if not task or not user or not user.email:
                # Mark as sent to avoid reprocessing broken rows
                r.sent = True
                continue

            subject = f"[VoiceNudge] Reminder: {task.title or task.text}"

            gcal_link = build_calendar_link(task)

            # Plain-text fallback body
            body_lines = [
                f"Hi {user.name or ''},",
                "",
                "This is your reminder for:",
                f"- {task.title or task.text}",
                f"Due at (UTC): {task.due_at}",
            ]
            if gcal_link:
                body_lines += [
                    "",
                    "Add to your Google Calendar:",
                    gcal_link,
                ]
            body_lines.append("")
            body_lines.append("— VoiceNudge")
            body = "\n".join(body_lines)

            # Simple HTML version with a button-like link
            html = None
            if gcal_link:
                html = f"""
                <p>Hi {user.name or ''},</p>
                <p>This is your reminder for:</p>
                <ul>
                    <li><strong>Task:</strong> {task.title or task.text}</li>
                    <li><strong>Due (UTC):</strong> {task.due_at}</li>
                </ul>
                <p>You can add this to your Google Calendar:</p>
                <p>
                    <a href="{gcal_link}"
                       style="display:inline-block;padding:10px 18px;
                              background-color:#4285F4;color:#ffffff;
                              text-decoration:none;border-radius:4px;">
                        Add to Google Calendar
                    </a>
                </p>
                <p>— VoiceNudge</p>
                """

            ok = send_email(app, user.email, subject, body, html=html)
            if ok:
                r.sent = True
                # Optional history audit
                try:
                    db.session.add(
                        TaskHistory(
                            user_id=user.id,
                            task_id=task.id,
                            text=getattr(task, "text", None),
                            title=getattr(task, "title", None),
                            due_at=getattr(task, "due_at", None),
                            category=getattr(task, "category", None),
                            priority=getattr(task, "priority", None),
                        )
                    )
                except Exception as hist_err:
                    print(f"⚠️ Could not write TaskHistory: {hist_err}")

        db.session.commit()


def init_scheduler(app):
    """Initialize and start APScheduler with a resilient interval job."""
    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.add_job(
            id="reminder_job",
            func=lambda: check_reminders(app),
            trigger="interval",
            minutes=1,
            # ✔ prevent small delays from skipping the run
            misfire_grace_time=60,
            # ✔ if multiple runs pile up, merge them into one run
            coalesce=True,
            # ✔ ensure only one instance runs at a time
            max_instances=1,
        )
        scheduler.start()
        print("✅ Reminder scheduler started")
