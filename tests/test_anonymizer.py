"""Tests for anonymization engine."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from anonymizer import anonymize_text, reset, BLOCKED_COMPANIES, BLOCKED_PEOPLE


def setup_function():
    """Reset anonymizer state before each test."""
    reset()


def test_anonymize_company_name():
    text = "We worked with Careium on this project."
    result = anonymize_text(text)
    assert "Careium" not in result
    assert "Company" in result or "Organization" in result


def test_anonymize_person_name():
    text = "Nicolas Waern presented the methodology."
    result = anonymize_text(text)
    assert "Nicolas Waern" not in result
    assert "Stakeholder" in result or "Lead" in result or "Sponsor" in result


def test_anonymize_email():
    text = "Contact us at test@example.com for details."
    result = anonymize_text(text)
    assert "test@example.com" not in result
    assert "[email redacted]" in result


def test_anonymize_phone():
    text = "Call +46 70 123 4567 for info."
    result = anonymize_text(text)
    assert "+46 70 123 4567" not in result
    assert "[phone redacted]" in result


def test_anonymize_percentage():
    text = "We achieved 23.7% improvement."
    result = anonymize_text(text)
    assert "23.7%" not in result
    assert "~" in result


def test_anonymize_currency():
    text = "The project cost $1,500,000 total."
    result = anonymize_text(text)
    assert "$1,500,000" not in result
    assert "~$2M" in result or "~$1M" in result


def test_anonymize_preserves_clean_text():
    text = "Digital twins use sensors to model reality."
    result = anonymize_text(text)
    assert result == text


def test_anonymize_case_insensitive():
    text = "CAREIUM is a company."
    result = anonymize_text(text)
    assert "CAREIUM" not in result


def test_anonymize_extra_companies():
    text = "Acme Corp did the work."
    result = anonymize_text(text, extra_companies=["Acme Corp"])
    assert "Acme Corp" not in result


def test_anonymize_extra_people():
    text = "John Smith led the project."
    result = anonymize_text(text, extra_people=["John Smith"])
    assert "John Smith" not in result


def test_reset_clears_state():
    anonymize_text("Careium test")
    reset()
    # After reset, next anonymization should start fresh
    result = anonymize_text("Careium again")
    assert "Careium" not in result


def test_blocklist_loaded():
    assert len(BLOCKED_COMPANIES) > 0
    assert len(BLOCKED_PEOPLE) > 0
    assert "Nicolas Waern" in BLOCKED_PEOPLE


def test_thread_safety():
    """Run multiple anonymizations concurrently to check for race conditions."""
    import threading
    errors = []

    def run():
        try:
            for _ in range(50):
                anonymize_text("Careium and Nicolas Waern worked together.")
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=run) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Thread-safety errors: {errors}"
