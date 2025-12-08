# tests/test_model_service.py
from voicenudge.ml import model_service


def test_predict_category_works_without_model(monkeypatch):
    # Simulate no model loaded
    monkeypatch.setattr(model_service, "category_model", None)
    result = model_service.predict_category("Some random task")
    # Fallback is "Personal" in your code
    assert isinstance(result, str)


def test_predict_priority_works_without_model(monkeypatch):
    monkeypatch.setattr(model_service, "priority_model", None)
    result = model_service.predict_priority("Some random task")
    # Fallback is "Medium" in your code
    assert isinstance(result, str)


def test_predict_category_with_dummy_model(monkeypatch):
    class DummyModel:
        def predict(self, X):
            return ["Work"]

    monkeypatch.setattr(model_service, "category_model", DummyModel())
    result = model_service.predict_category("Finish project report")
    assert result == "Work"


def test_predict_priority_with_dummy_model(monkeypatch):
    class DummyModel:
        def predict(self, X):
            return ["High"]

    monkeypatch.setattr(model_service, "priority_model", DummyModel())
    result = model_service.predict_priority("Urgent call customer")
    assert result == "High"
