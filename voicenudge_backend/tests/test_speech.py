# tests/test_speech.py
"""
Tests for speech-related utilities:
- Whisper STT wrapper (transcribe_audio)
- VoiceAuth.compare_embeddings math (no model load)
"""

import pytest


# -----------------------------
# Whisper STT: transcribe_audio
# -----------------------------

def test_transcribe_audio_translate_true(monkeypatch, tmp_path):
    """
    transcribe_audio() should call model.transcribe with task='translate'
    when translate=True.
    We stub whisper.load_model BEFORE importing whisper_stt so no real
    weights are loaded.
    """
    # Fake audio file
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"fake audio")

    calls = {}

    # 1) Stub whisper.load_model globally
    import whisper

    class FakeModel:
        def transcribe(self, path, task):
            calls["path"] = path
            calls["task"] = task
            return {"text": "Hello from Whisper"}

    monkeypatch.setattr(whisper, "load_model", lambda size: FakeModel())

    # 2) Now import whisper_stt (will use FakeModel)
    import importlib
    from voicenudge.speech import whisper_stt
    importlib.reload(whisper_stt)

    text = whisper_stt.transcribe_audio(str(audio_file), translate=True)

    assert text == "Hello from Whisper"
    assert calls["path"] == str(audio_file)
    assert calls["task"] == "translate"


def test_transcribe_audio_translate_false(monkeypatch, tmp_path):
    """
    Same as above, but translate=False → task='transcribe'.
    """
    audio_file = tmp_path / "sample2.wav"
    audio_file.write_bytes(b"fake audio 2")

    calls = {}

    import whisper

    class FakeModel:
        def transcribe(self, path, task):
            calls["path"] = path
            calls["task"] = task
            return {"text": "Original language text"}

    monkeypatch.setattr(whisper, "load_model", lambda size: FakeModel())

    import importlib
    from voicenudge.speech import whisper_stt
    importlib.reload(whisper_stt)

    text = whisper_stt.transcribe_audio(str(audio_file), translate=False)

    assert text == "Original language text"
    assert calls["path"] == str(audio_file)
    assert calls["task"] == "transcribe"


# -----------------------------------------
# VoiceAuth.compare_embeddings (no model)
# -----------------------------------------

def test_voiceauth_compare_embeddings_identical_vectors():
    """
    Test cosine similarity logic without loading SpeechBrain.
    We bypass __init__ using object.__new__().
    """
    from voicenudge.auth import voice_auth as va_module

    va = object.__new__(va_module.VoiceAuth)

    emb1 = [1.0, 0.0, 0.0]
    emb2 = [1.0, 0.0, 0.0]

    score = va.compare_embeddings(emb1, emb2)
    assert pytest.approx(score, rel=1e-6) == 1.0


def test_voiceauth_compare_embeddings_orthogonal_vectors():
    """
    Cosine similarity of orthogonal vectors ≈ 0.
    """
    from voicenudge.auth import voice_auth as va_module

    va = object.__new__(va_module.VoiceAuth)

    emb1 = [1.0, 0.0]
    emb2 = [0.0, 1.0]

    score = va.compare_embeddings(emb1, emb2)
    assert abs(score) < 1e-5
