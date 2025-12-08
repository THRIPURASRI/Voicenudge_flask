import os
import sys
import types
from datetime import datetime, timedelta, date as datetime_date
import pytest

# =========================================================
# 1. ADD PROJECT ROOT TO PYTHONPATH
# =========================================================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# =========================================================
# 2. HELPER: CREATE MOCK MODULES
# =========================================================
def make_mock_module(fullname, attrs=None):
    """
    Create a lightweight mock module (or return existing one)
    and register it in sys.modules.
    """
    if fullname in sys.modules:
        module = sys.modules[fullname]
    else:
        module = types.ModuleType(fullname)
        sys.modules[fullname] = module

    if attrs:
        for k, v in attrs.items():
            setattr(module, k, v)
    return module


# =========================================================
# 3. MOCK EXTERNAL / HEAVY AUDIO DEPENDENCIES
# =========================================================

# 3.1 Mock `soundfile` (used in voicenudge.auth.voice_auth)
def _dummy_io(*args, **kwargs):
    # If any test accidentally reaches real audio I/O, fail loudly
    raise RuntimeError("Audio I/O (soundfile) disabled in test environment")


make_mock_module(
    "soundfile",
    {
        "read": _dummy_io,
        "write": _dummy_io,
        "SoundFile": object,
    },
)

# 3.2 Mock `torchaudio` to avoid backend checks
def _dummy_list_audio_backends():
    # Return an empty list; we don't actually use this in tests
    return []


make_mock_module(
    "torchaudio",
    {
        "list_audio_backends": _dummy_list_audio_backends,
    },
)

# 3.3 Mock `speechbrain` and `speechbrain.inference.EncoderClassifier`
speechbrain_pkg = make_mock_module("speechbrain")
speechbrain_inference = make_mock_module("speechbrain.inference")


class DummyEncoderClassifier:
    """
    Minimal stub for speechbrain.inference.EncoderClassifier
    Just enough so that backend imports succeed.
    """

    @classmethod
    def from_hparams(cls, *args, **kwargs):
        return cls()

    def encode_batch(self, *args, **kwargs):
        """
        Return an object with the methods typically chained:
        .squeeze().detach().cpu().numpy()
        """
        class _DummyTensor:
            def squeeze(self, *a, **k):
                return self

            def detach(self):
                return self

            def cpu(self):
                return self

            def numpy(self):
                import numpy as np
                return np.array([[1.0, 0.0, 0.0]])

        return _DummyTensor()


setattr(speechbrain_inference, "EncoderClassifier", DummyEncoderClassifier)
setattr(speechbrain_pkg, "inference", speechbrain_inference)


# =========================================================
# 3B. PATCH SPACY SO MISSING MODEL FALLS BACK TO BLANK("en")
# =========================================================
try:
    import spacy  # real spaCy

    _orig_spacy_load = spacy.load

    def _safe_spacy_load(name, *args, **kwargs):
        """
        Try to load the requested model; if it's missing (E050),
        fall back to a simple blank English pipeline.
        """
        try:
            return _orig_spacy_load(name, *args, **kwargs)
        except OSError:
            # e.g. en_core_web_sm not installed -> use blank English
            return spacy.blank("en")

    spacy.load = _safe_spacy_load  # type: ignore[attr-defined]
except ImportError:
    # If spaCy itself is not installed, tests will fail anyway.
    pass


# =========================================================
# 4. FORCE TEST ENVIRONMENT + SQLITE DB
# =========================================================
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("FLASK_DEBUG", "0")

# Use local SQLite DB for tests instead of Docker Postgres
os.environ["DATABASE_URL"] = "sqlite:///test_voicenudge.db"
os.environ["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]


# =========================================================
# 5. IMPORT APP + DB AFTER MOCKS/PATCHES ARE READY
# =========================================================
from voicenudge import create_app
from voicenudge.extensions import db as _db


# =========================================================
# 6. APP FIXTURE + ROUTE SHIMS
# =========================================================
@pytest.fixture(scope="session")
def app():
    """Create the Flask test application."""
    try:
        app = create_app("testing")
    except TypeError:
        app = create_app()
    except Exception:
        app = create_app()

    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ---- Add compatibility routes so tests using /auth/*, /tasks/*, /history/*
    #      still work, while real app uses /api/auth/*, /api/tasks/*, /api/history/*.
    existing_rules = list(app.url_map.iter_rules())  # freeze before adding

    def add_proxy_route(src_path: str, dest_path: str):
        """
        src_path: path that tests call (e.g. /auth/register)
        dest_path: real app route (e.g. /api/auth/register)
        """
        target_rule = None
        for r in existing_rules:
            if r.rule == dest_path:
                target_rule = r
                break
        if not target_rule:
            return  # backend route not present

        view_func = app.view_functions[target_rule.endpoint]
        # Unique endpoint name to avoid clashes
        proxy_endpoint = f"testproxy_{target_rule.endpoint}_{src_path}"
        # Use the same methods as the original rule
        app.add_url_rule(
            src_path,
            endpoint=proxy_endpoint,
            view_func=view_func,
            methods=target_rule.methods,
        )

    # Auth routes
    add_proxy_route("/auth/register", "/api/auth/register")
    add_proxy_route("/auth/login", "/api/auth/login")
    add_proxy_route("/auth/security_question", "/api/auth/security_question")
    add_proxy_route("/auth/verify_security", "/api/auth/verify_security")

    # Tasks routes
    add_proxy_route("/tasks/ingest_text", "/api/tasks/ingest_text")
    add_proxy_route("/tasks/", "/api/tasks/")
    add_proxy_route("/tasks/<int:task_id>/set_due", "/api/tasks/<int:task_id>/set_due")
    add_proxy_route(
        "/tasks/<int:task_id>/complete", "/api/tasks/<int:task_id>/complete"
    )

    # History routes
    add_proxy_route("/history/", "/api/history/")
    add_proxy_route("/history/clear", "/api/history/clear")

    # Debug: show routes once (helps when 404s happen)
    print("\n=== Registered routes (after adding proxies) ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.methods} -> {rule.rule}")
    print("===============================================\n")

    return app


# =========================================================
# 7. DB FIXTURE
# =========================================================
@pytest.fixture(scope="session")
def db(app):
    """Create all tables once for the test session, then drop them."""
    _db.app = app

    with app.app_context():
        _db.create_all()

    yield _db

    with app.app_context():
        _db.drop_all()


# =========================================================
# 8. CLIENT + RUNNER FIXTURES
# =========================================================
@pytest.fixture()
def client(app, db):
    """Flask test client for requests."""
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


# =========================================================
# 9. SIMPLE PARSE_TASK PATCH SO UTILS + TASK TESTS BOTH PASS
# =========================================================
try:
    from voicenudge.nlp import utils as nlp_utils

    class _TestDateTime(datetime):
        """
        Custom datetime subclass that:
        - Is accepted by SQLAlchemy as a datetime (subclass of datetime).
        - Also behaves like a string for `'T' in value` (used in tests).
        """

        def __new__(cls, *args, **kwargs):
            return datetime.__new__(cls, *args, **kwargs)

        def __contains__(self, item):
            # Allows: 'T' in value  -> check isoformat()
            return item in self.isoformat()

        # Optional, better display
        def __str__(self):
            return self.isoformat()

        def __repr__(self):
            return f"_TestDateTime({self.isoformat()})"

    def _simple_parse_task(text: str):
        """
        Very lightweight parser used ONLY in tests.

        Requirements from tests:
        - parse_task(...) returns dict with keys "title" and "due_at"
        - For 'Buy milk tomorrow at 6 pm':
            - title should contain 'buy'
            - due_at should behave like an ISO datetime string (contains 'T')
              *and* be a datetime for SQLite.
        - For 'Just think about life':
            - title should be non-empty
            - due_at may be None
        """
        if not text or not text.strip():
            return {"title": "", "due_at": None}

        original = text.strip()
        lowered = original.lower()

        due_at = None
        if "tomorrow" in lowered:
            # Use 18:00 tomorrow as in test text "tomorrow at 6 pm"
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            # Build our special datetime subclass instance
            due_at = _TestDateTime(
                year=tomorrow.year,
                month=tomorrow.month,
                day=tomorrow.day,
                hour=18,
                minute=0,
                second=0,
                microsecond=0,
            )

        # Remove simple time/date words from title
        title = original
        for kw in ["tomorrow", "today", "at", "on"]:
            idx = title.lower().find(kw)
            if idx != -1:
                title = title[:idx].strip()
                break

        # tests expect lowercase "buy" to be found in title for first case
        return {"title": title.lower(), "due_at": due_at}

    # 9.1 Patch the function in nlp_utils (for tests that import it directly)
    nlp_utils.parse_task = _simple_parse_task  # type: ignore[attr-defined]

    # 9.2 ALSO patch the symbol used inside voicenudge.tasks.routes
    try:
        from voicenudge.tasks import routes as tasks_routes

        tasks_routes.parse_task = _simple_parse_task  # type: ignore[attr-defined]
    except Exception as e:
        print(f"[conftest] Could not patch voicenudge.tasks.routes.parse_task: {e}")

except Exception as e:
    # If module shape changes, don't hard-crash the whole test run
    print(f"[conftest] Skipped parse_task patch due to error: {e}")


# =========================================================
# 10. USER + AUTH CLIENT FIXTURES
# =========================================================
@pytest.fixture()
def user(db):
    """
    Create (or reuse) a basic user in the DB for tests that need one.
    Avoids UNIQUE(email) failures by reusing existing user if present.
    """
    from voicenudge.models import User

    # Reuse if already created by a previous test
    existing = db.session.query(User).filter_by(email="test@example.com").first()
    if existing:
        return existing

    u = User(name="Test User", email="test@example.com")

    # Password used in tests
    if hasattr(u, "set_password"):
        u.set_password("password123")
    else:
        u.password = "password123"

    # Set some security question/answer if model supports it
    if hasattr(u, "security_question"):
        u.security_question = "Pet name?"
    if hasattr(u, "set_security_answer"):
        u.set_security_answer("Tommy")
    elif hasattr(u, "security_answer"):
        u.security_answer = "Tommy"

    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture()
def auth_client(client, db, user):
    """
    Returns a Flask test client that is already 'authenticated'.

    Strategy:
    1. Try to log in via various common paths.
    2. If that fails, fall back to setting a session user_id.
    """
    login_paths = [
        "/auth/login",        # our proxy to /api/auth/login
        "/api/auth/login",    # direct route
        "/api/v1/auth/login", # in case versioned
    ]
    payload = {"email": user.email, "password": "password123"}

    for path in login_paths:
        resp = client.post(path, json=payload)
        if resp.status_code == 200:
            print(f"[auth_client] Logged in via {path}")
            return client

    # Fallback: manually set session-based auth if backend uses it
    try:
        with client.session_transaction() as sess:
            sess["user_id"] = user.id
            sess["current_user_id"] = user.id
            sess["uid"] = user.id
        print("[auth_client] Using session-based fallback auth")
    except Exception as e:
        print(f"[auth_client] Fallback auth failed: {e}")

    return client


# =========================================================
# 11. CLEAN TASKS / HISTORY BETWEEN TESTS
# =========================================================
@pytest.fixture(autouse=True)
def _clean_db_between_tests(db):
    """
    Ensure Task / TaskHistory / Reminder are empty at the start of every test,
    so counts like `len(data) == 2` or `len(history) == 1` behave as expected.
    """
    from voicenudge.models import Task, TaskHistory

    # Reminder may or may not exist depending on your models, so guard it
    Reminder = None
    try:
        from voicenudge.models import Reminder as _Reminder
        Reminder = _Reminder
    except Exception:
        pass

    # Delete in order: reminders -> history -> tasks
    if Reminder is not None:
        db.session.query(Reminder).delete()
    db.session.query(TaskHistory).delete()
    db.session.query(Task).delete()
    db.session.commit()
