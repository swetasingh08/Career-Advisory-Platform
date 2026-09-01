from agents import detect_intent, orchestrator
from utils import estimate_score


def test_detect_resume_intent():
    intent, agents = detect_intent("Improve my resume for a Python job")
    assert intent == "Resume Improvement"
    assert "resume" in agents


def test_estimate_score():
    assert estimate_score("Resume Score: 82/100") == 82
    assert estimate_score("No score here", default=70) == 70


def test_orchestrator_demo_response_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = orchestrator("How can I improve my resume?")
    assert "Resume Agent" in result["agent"]
    assert "response" in result
