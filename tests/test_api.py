"""Integration tests for the FastAPI application."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# --- Health ---
def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["knowledge_entries"] > 0
    assert data["smile_phases"] > 0


# --- Search ---
def test_search_basic():
    r = client.get("/api/search?q=digital+twin")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] > 0
    assert len(data["results"]) > 0


def test_search_empty_query():
    r = client.get("/api/search?q=")
    assert r.status_code == 422  # validation error


def test_search_limit():
    r = client.get("/api/search?q=twin&limit=2")
    assert r.status_code == 200
    assert len(r.json()["results"]) <= 2


def test_search_limit_too_high():
    r = client.get("/api/search?q=twin&limit=100")
    assert r.status_code == 422


# --- Chat ---
def test_chat_basic():
    r = client.post("/api/chat", json={
        "question": "What is a digital twin?",
        "message_count": 0,
    })
    assert r.status_code == 200
    data = r.json()
    assert len(data["answer"]) > 0
    assert isinstance(data["sources"], list)


def test_chat_empty_question():
    r = client.post("/api/chat", json={
        "question": "",
        "message_count": 0,
    })
    assert r.status_code == 422


def test_chat_question_too_long():
    r = client.post("/api/chat", json={
        "question": "x" * 2001,
        "message_count": 0,
    })
    assert r.status_code == 422


def test_chat_invalid_spin_action():
    r = client.post("/api/chat", json={
        "question": "",
        "spin_action": "hack",
    })
    assert r.status_code == 422


# --- SPIN Flow ---
def test_spin_start():
    r = client.post("/api/chat", json={
        "question": "",
        "spin_action": "start",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["spin"]["type"] == "spin_question"
    assert data["spin"]["phase"] == "situation"


def test_spin_answer():
    r = client.post("/api/chat", json={
        "question": "",
        "spin_action": "answer",
        "spin_state": {"phase_index": 0, "answers": {}},
        "spin_value": "enterprise",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["spin"]["phase"] == "situation"  # Still in situation phase (s2)
    assert data["spin"]["answers"]["s1_org_type"] == "enterprise"


def test_spin_invalid_value():
    r = client.post("/api/chat", json={
        "question": "",
        "spin_action": "answer",
        "spin_state": {"phase_index": 0, "answers": {}},
        "spin_value": "invalid_option",
    })
    assert r.status_code == 422


def test_spin_full_flow():
    # Start
    r = client.post("/api/chat", json={"question": "", "spin_action": "start"})
    state = r.json()["spin"]

    # Answer all 9 phases
    answers = [
        "startup", "manufacturing", "pilot",       # situation (s1, s2, s3)
        "slow_decisions", "partial",                # problem (p1, p2)
        "missed_opportunity", "leadership",         # implication (i1, i2)
        "new_revenue", "implementation_plan",       # need (n1, n2)
    ]
    for value in answers:
        r = client.post("/api/chat", json={
            "question": "",
            "spin_action": "answer",
            "spin_state": state,
            "spin_value": value,
        })
        assert r.status_code == 200
        state = r.json()["spin"]

    assert state["type"] == "spin_complete"
    assert "product" in state
    assert state["product"]["id"] == "workshop"
    # Summary should be in the answer text
    assert "**" in r.json()["answer"]  # Contains markdown formatting


# --- SMILE ---
def test_smile_overview():
    r = client.get("/api/smile")
    assert r.status_code == 200
    data = r.json()
    assert len(data["phases"]) == 6


def test_smile_phase_not_found():
    r = client.get("/api/smile/nonexistent")
    assert r.status_code == 404


# --- Resources ---
def test_resources():
    r = client.get("/api/resources")
    assert r.status_code == 200
    data = r.json()
    assert len(data["resources"]) > 0


# --- CTA triggers ---
def test_cta_on_personalization():
    r = client.post("/api/chat", json={
        "question": "How should my company approach digital twins?",
        "message_count": 1,
    })
    data = r.json()
    assert data["cta"] is not None
    assert data["cta"]["type"] == "spin_offer"
    assert data["cta"]["cta_action"] == "spin_start"


def test_cta_on_depth():
    r = client.post("/api/chat", json={
        "question": "Tell me about interoperability",
        "message_count": 6,
    })
    data = r.json()
    assert data["cta"] is not None
    assert "spin_start" in data["cta"].get("cta_action", "")
