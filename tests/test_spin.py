"""Tests for SPIN assessment engine (expanded 9-phase version)."""
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


def _run_full_flow(answers_list):
    """Helper: run through all phases with given answer values."""
    r = advance_spin(None, None)
    for val in answers_list:
        r = advance_spin(r, val)
    return r


def test_spin_full_flow_workshop():
    """Mid-market wanting implementation plan → workshop."""
    r = _run_full_flow([
        "mid_market",       # s1: org type
        "manufacturing",    # s2: industry
        "pilot",            # s3: maturity
        "no_visibility",    # p1: challenge
        "partial",          # p2: attempted
        "competitive_risk", # i1: consequence
        "my_team",          # i2: stakeholders
        "reduce_cost",      # n1: desired outcome
        "build_mvt",        # n2: next step
    ])
    assert r["type"] == "spin_complete"
    assert r["product"]["id"] == "workshop"
    assert "summary" in r


def test_spin_full_flow_lecture():
    """Enterprise wanting to inspire team → lecture."""
    r = _run_full_flow([
        "enterprise",       # s1
        "energy",           # s2
        "curious",          # s3
        "siloed_data",      # p1
        "never",            # p2
        "cost_increase",    # i1
        "leadership",       # i2
        "understand",       # n1
        "inspire_team",     # n2
    ])
    assert r["type"] == "spin_complete"
    assert r["product"]["id"] == "lecture"


def test_spin_full_flow_strategy():
    """Individual exploring → strategy session."""
    r = _run_full_flow([
        "individual",       # s1
        "other",            # s2
        "curious",          # s3
        "dont_know_where",  # p1
        "never",            # p2
        "status_quo",       # i1
        "just_me",          # i2
        "understand",       # n1
        "explore",          # n2
    ])
    assert r["type"] == "spin_complete"
    assert r["product"]["id"] == "strategy"


def test_spin_answers_accumulate():
    r = advance_spin(None, None)
    r = advance_spin(r, "startup")
    assert r["answers"]["s1_org_type"] == "startup"
    r = advance_spin(r, "healthcare")
    assert r["answers"]["s2_industry"] == "healthcare"
    assert r["answers"]["s1_org_type"] == "startup"


def test_spin_phase_count():
    assert len(SPIN_PHASES) == 9
    assert len(PHASE_ORDER) == 9


def test_spin_all_phases_have_options():
    for phase in SPIN_PHASES:
        assert len(phase["options"]) >= 3
        assert "question" in phase
        assert "phase" in phase
        assert "id" in phase
        for opt in phase["options"]:
            assert "value" in opt
            assert "label" in opt


def test_spin_summary_generated():
    """Summary should contain markdown and industry-specific content."""
    r = _run_full_flow([
        "enterprise", "real_estate", "researching",
        "vendor_lock", "failed",
        "compliance_risk", "whole_org",
        "sustainability", "implementation_plan",
    ])
    assert r["type"] == "spin_complete"
    assert "summary" in r
    summary = r["summary"]
    assert "**" in summary  # Contains markdown bold
    assert len(summary) > 200  # Substantive


def test_spin_phases_cover_all_spin_categories():
    """Verify we have Situation, Problem, Implication, and Need phases."""
    phases_seen = set(p["phase"] for p in SPIN_PHASES)
    assert phases_seen == {"situation", "problem", "implication", "need"}
