# tests/test_auth.py
import json
from voicenudge.models import User


def test_register_basic(client, db):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secret123",
        "security_question": "Pet name?",
        "security_answer": "Tommy"
    }

    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert "message" in data

    # user in DB
    user = User.query.filter_by(email="alice@example.com").first()
    assert user is not None
    assert user.check_password("secret123")
    assert user.security_question == "Pet name?"


def test_register_missing_fields(client):
    payload = {
        "name": "Bob",
        "email": "bob@example.com",
        # missing password, question, answer
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_login_without_voice_first_time(client, db):
    # Create user with password and no voice embedding
    from voicenudge.models import User

    u = User(name="NoVoice", email="novoice@example.com")
    u.set_password("testpass")
    db.session.add(u)
    db.session.commit()

    payload = {"email": "novoice@example.com", "password": "testpass"}
    resp = client.post("/auth/login", json=payload)

    assert resp.status_code == 200
    data = resp.get_json()
    assert "Login successful" in data["message"]


def test_login_invalid_credentials(client, db):
    payload = {"email": "nosuch@example.com", "password": "whatever"}
    resp = client.post("/auth/login", json=payload)
    assert resp.status_code == 401
    assert "error" in resp.get_json()


def test_get_security_question(client, db):
    from voicenudge.models import User
    u = User(name="SQUser", email="sq@example.com")
    u.set_password("pass")
    u.security_question = "Your city?"
    db.session.add(u)
    db.session.commit()

    resp = client.get("/auth/security_question?email=sq@example.com")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["security_question"] == "Your city?"


def test_verify_security_success(client, db):
    from voicenudge.models import User
    u = User(name="SQUser2", email="sq2@example.com")
    u.set_password("pass")
    u.security_question = "Your school?"
    u.set_security_answer("RVCE")
    db.session.add(u)
    db.session.commit()

    resp = client.post(
        "/auth/verify_security",
        json={"email": "sq2@example.com", "answer": "rvce"},
    )
    assert resp.status_code == 200
    assert "Login successful" in resp.get_json()["message"]


def test_verify_security_fail(client, db):
    from voicenudge.models import User
    u = User(name="SQUser3", email="sq3@example.com")
    u.set_password("pass")
    u.security_question = "Your school?"
    u.set_security_answer("RVCE")
    db.session.add(u)
    db.session.commit()

    resp = client.post(
        "/auth/verify_security",
        json={"email": "sq3@example.com", "answer": "wrong"},
    )
    assert resp.status_code == 401
    assert "Incorrect security answer" in resp.get_json()["error"]
