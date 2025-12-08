from datetime import datetime
from voicenudge.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🆕 Voice Authentication Fields
    voice_embedding = db.Column(db.PickleType, nullable=True)  # stores extracted voice embedding vector
    voice_locked = db.Column(db.Boolean, default=False)        # lock flag for unauthorized access

    # Relationships
    tasks = db.relationship("Task", backref="user", lazy=True, cascade="all,delete")
    reminders = db.relationship("Reminder", backref="user", lazy=True, cascade="all,delete")
    history = db.relationship("TaskHistory", backref="user", lazy=True, cascade="all,delete")

    # Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    # 🧠 Security Question (fallback for voice mismatch)
    security_question = db.Column(db.String(255), nullable=True)
    security_answer_hash = db.Column(db.String(255), nullable=True)

    def set_security_answer(self, answer):
        """Hash and store the answer (case-insensitive)."""
        self.security_answer_hash = generate_password_hash(answer.lower())

    def check_security_answer(self, answer):
        """Verify security question answer."""
        if not self.security_answer_hash:
            return False
        return check_password_hash(self.security_answer_hash, answer.lower())



class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  

    # Task content
    text = db.Column(db.Text, nullable=False)            # Always English (for NLP/ML)
    original_text = db.Column(db.Text, nullable=True)    # Native transcription if available
    title = db.Column(db.String(255), nullable=False)

    # Metadata
    due_at = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reminders = db.relationship("Reminder", backref="task", lazy=True, cascade="all,delete")


class TaskHistory(db.Model):
    __tablename__ = "task_history"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)   # ensures history is per-user
    task_id = db.Column(db.Integer)  # optional, to reference original task id

    # Snapshot of task details
    text = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    due_at = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)


class Reminder(db.Model):
    __tablename__ = "reminders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)

    # Reminder details
    remind_at = db.Column(db.DateTime, nullable=False, index=True)
    channel = db.Column(db.String(16), default="email")
    sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
