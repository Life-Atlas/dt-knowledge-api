"""Tests for knowledge store search."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from knowledge import KnowledgeStore


def get_store():
    return KnowledgeStore()


def test_store_loads_data():
    s = get_store()
    assert len(s.entries) > 0
    assert len(s.case_studies) > 0
    assert len(s.smile.get("phases", [])) > 0


def test_search_returns_results():
    s = get_store()
    results = s.search("digital twin")
    assert len(results) > 0
    assert results[0].score > 0


def test_search_empty_query():
    s = get_store()
    results = s.search("")
    assert results == []


def test_search_respects_limit():
    s = get_store()
    results = s.search("digital twin", limit=2)
    assert len(results) <= 2


def test_search_hides_paid_by_default():
    s = get_store()
    results = s.search("digital twin", limit=20)
    for r in results:
        assert r.tier != "paid"


def test_search_beginner_boost():
    """Beginner questions should return intro content first."""
    s = get_store()
    results = s.search("How should I start with digital twins?")
    assert len(results) > 0
    assert "Getting Started" in results[0].title or "beginner" in results[0].tags


def test_search_smile_query():
    """SMILE-specific queries should return SMILE content, not beginner."""
    s = get_store()
    results = s.search("What is the SMILE methodology?")
    assert len(results) > 0
    assert "SMILE" in results[0].title


def test_search_edge_query():
    s = get_store()
    results = s.search("edge computing")
    assert len(results) > 0
    assert any("edge" in r.title.lower() for r in results[:3])


def test_search_stop_words_filtered():
    """Common words like 'the', 'is', 'a' shouldn't inflate scores."""
    s = get_store()
    r1 = s.search("edge")
    r2 = s.search("the edge is a")
    # Both should find edge content in top results
    r1_titles = {r.title for r in r1[:3]}
    r2_titles = {r.title for r in r2[:3]}
    assert len(r1_titles.intersection(r2_titles)) >= 1, "Edge content should appear in both"


def test_smile_overview():
    s = get_store()
    overview = s.get_smile_overview()
    assert "phases" in overview
    assert len(overview["phases"]) == 6


def test_smile_phase_detail():
    s = get_store()
    phases = s.smile.get("phases", [])
    assert len(phases) > 0
    phase = s.get_phase_detail(phases[0]["id"])
    assert phase is not None
    assert "name" in phase


def test_smile_phase_not_found():
    s = get_store()
    assert s.get_phase_detail("nonexistent") is None


def test_has_paid_matches():
    s = get_store()
    # Should not crash even if no paid content exists
    result = s.has_paid_matches("anything")
    assert isinstance(result, bool)
