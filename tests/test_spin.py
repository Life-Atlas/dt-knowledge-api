"""Tests for SPIN questionnaire engine."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from spin import advance_spin, SPIN_PHASES, PHASE_ORDER


def test_spin_start():
    result = advance_spin(None, None)
    assert result["type"] == "spin_question"
    assert result["phase"] == "situation"
    assert result["phase_index"] == 0
    assert len(result["options"]) >= 3
    assert result["answers"] == {}


def test_spin_full_flow_workshop():
    """Mid-market + build_mvt should recommend workshop."""
    r = advance_spin(None, None)
    r = advance_spin(r, "mid_market")
    assert r["phase"] == "problem"
    r = advance_spin(r, "no_visibility")
    assert r["phase"] == "implication"
    r = advance_spin(r, "competitive_risk")
    assert r["phase"] == "need"
    r = advance_spin(r, "build_mvt")
    assert r["type"] == "spin_complete"
    assert r["product"]["id"] == "workshop"


def test_spin_full_flow_lecture():
    """Enterprise + inspire_team should recommend lecture."""
    r = advance_spin(None, None)
    r = advance_spin(r, "enterprise")
    r = advance_spin(r, "siloed_data")
    r = advance_spin(r, "cost_increase")
    r = advance_spin(r, "inspire_team")
    assert r["type"] == "spin_complete"
    assert r["product"]["id"] == "lecture"


def test_spin_full_flow_strategy():
    """Individual + explore should recommend free strategy session."""
    r = advance_spin(None, None)
    r = advance_spin(r, "individual")
    r = advance_spin(r, "dont_know_where")
    r = advance_spin(r, "status_quo")
    r = advance_spin(r, "explore")
    assert r["type"] == "spin_complete"
    assert r["product"]["id"] == "strategy"
    assert r["product"]["price"] == "Free"


def test_spin_answers_accumulate():
    r = advance_spin(None, None)
    r = advance_spin(r, "startup")
    assert r["answers"]["situation"] == "startup"
    r = advance_spin(r, "slow_decisions")
    assert r["answers"]["problem"] == "slow_decisions"
    assert r["answers"]["situation"] == "startup"


def test_spin_phase_count():
    assert len(SPIN_PHASES) == 4
    assert len(PHASE_ORDER) == 4


def test_spin_all_phases_have_options():
    for phase in SPIN_PHASES:
        assert len(phase["options"]) >= 3
        assert "question" in phase
        assert "phase" in phase
        for opt in phase["options"]:
            assert "value" in opt
            assert "label" in opt
