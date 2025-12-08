from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    unset_jwt_cookies, set_access_cookies
)
from datetime import timedelta
from ..extensions import db
from ..models import User
from .voice_auth import VoiceAuth
import numpy as np
import os

auth_bp = Blueprint("auth", __name__)
voice_auth = VoiceAuth()


# --------------------------- REGISTER ---------------------------
@auth_bp.post("/register")
def register():
    """Register user with password, voice, and security question."""
    data = request.form or request.get_json() or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    question = data.get("security_question")
    answer = data.get("security_answer")

    if not all([name, email, password, question, answer]):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(name=name, email=email)
    user.set_password(password)
    user.security_question = question
    user.set_security_answer(answer)

    # ✅ Save voice embedding (Docker-safe)
    if "voice" in request.files:
        file = request.files["voice"]
        save_dir = os.path.join(os.getcwd(), "temp_voices")
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, file.filename)
        file.save(path)
        print(f"🎵 Saved registration voice to: {path}")

        embedding = voice_auth.get_embedding(path)
        if embedding is not None:
            user.voice_embedding = embedding.tolist()

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully ✅"}), 201


# --------------------------- LOGIN ---------------------------
@auth_bp.post("/login")
def login():
    """Login using password and voice (with fallback to security question)."""
    data = request.form or request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # 🟢 Case 1: User has no voice sample (first time)
    if not user.voice_embedding:
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=3))
        resp = jsonify({"message": "Login successful ✅ (no voice sample yet)"})
        set_access_cookies(resp, token)
        return resp

    # 🟢 Case 2: Voice-based authentication
    if "voice" not in request.files:
        return jsonify({
            "message": "Voice sample required.",
            "security_question": user.security_question
        }), 206

    file = request.files["voice"]

    # ✅ Docker-safe voice save
    save_dir = os.path.join(os.getcwd(), "temp_voices")
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, file.filename)
    file.save(path)
    print(f"🎤 Saved login voice sample to: {path}")

    try:
        test_embedding = voice_auth.get_embedding(path)
        stored_embedding = np.array(user.voice_embedding, dtype=np.float32)
        score = voice_auth.compare_embeddings(test_embedding, stored_embedding)
    except Exception as e:
        return jsonify({"error": f"Voice processing failed: {str(e)}"}), 500

    # 🧠 Decision Logic
    if score >= 0.75:
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=3))
        resp = jsonify({
            "message": f"Login successful ✅ (voice match {score:.2f})",
            "similarity": float(score)
        })
        set_access_cookies(resp, token)
        return resp

    elif 0.55 <= score < 0.75:
        return jsonify({
            "message": "Voice uncertain — please answer your security question.",
            "security_question": user.security_question
        }), 206

    else:
        user.voice_locked = True
        db.session.commit()
        return jsonify({"error": "Voice mismatch — account locked 🔒"}), 403


# --------------------------- SECURITY QUESTION VERIFY ---------------------------
@auth_bp.post("/verify_security")
def verify_security():
    """Fallback verification when voice slightly mismatched."""
    data = request.get_json() or {}
    email = data.get("email")
    answer = data.get("answer")

    user = User.query.filter_by(email=email).first()
    if not user or not answer:
        return jsonify({"error": "Invalid request"}), 400

    if user.check_security_answer(answer):
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=3))
        resp = jsonify({"message": "Login successful ✅ via security question"})
        set_access_cookies(resp, token)
        return resp

    return jsonify({"error": "Incorrect security answer"}), 401


# --------------------------- SECURITY QUESTION FETCH ---------------------------
@auth_bp.get("/security_question")
def get_security_question():
    """Return stored question for a given email."""
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"security_question": user.security_question})


# --------------------------- LOGOUT ---------------------------
@auth_bp.post("/logout")
@jwt_required()
def logout():
    resp = jsonify({"message": "Logged out"})
    unset_jwt_cookies(resp)
    return resp


# --------------------------- CURRENT USER ---------------------------
@auth_bp.get("/me")
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "voice_locked": user.voice_locked
    })
