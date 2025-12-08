# tests/test_utils.py
from voicenudge.nlp.utils import clean_text, parse_task


def test_clean_text_basic():
    assert clean_text("  Hello   WORLD  ") == "hello world"
    assert clean_text("") == ""
    assert clean_text("  ") == ""


def test_parse_task_with_tomorrow():
    result = parse_task("Buy milk tomorrow at 6 pm")
    assert "title" in result
    assert "due_at" in result
    assert "buy" in result["title"]
    # due_at is ISO string or None
    if result["due_at"] is not None:
        assert "T" in result["due_at"]  # ISO format


def test_parse_task_no_date():
    result = parse_task("Just think about life")
    assert "title" in result
    # Date might be None if nothing parseable
    # Just check no crash and title non-empty
    assert result["title"] != ""
