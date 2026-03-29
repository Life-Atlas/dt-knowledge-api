"""
Privacy/Anonymization engine for the Digital Twin Knowledge API.
Strips identifiable information from content before public exposure.

Ported from LPI MCP Server (TypeScript) with extensions.
"""
import re
import json
import os

COMPANY_LABELS = [
    "Company A", "Company B", "Company C", "Company D",
    "Organization Alpha", "Organization Beta", "Organization Gamma",
]

PERSON_LABELS = [
    "Stakeholder 1", "Stakeholder 2", "Stakeholder 3",
    "Client Lead", "Project Sponsor", "Technical Lead",
]

_company_map: dict[str, str] = {}
_person_map: dict[str, str] = {}
_company_counter = 0
_person_counter = 0

# Load blocklist of known names to always anonymize
_blocklist_path = os.path.join(os.path.dirname(__file__), "data", "blocklist.json")
BLOCKLIST: dict = {}
if os.path.exists(_blocklist_path):
    with open(_blocklist_path) as f:
        BLOCKLIST = json.load(f)

BLOCKED_COMPANIES = BLOCKLIST.get("companies", [])
BLOCKED_PEOPLE = BLOCKLIST.get("people", [])


def anonymize_company(name: str) -> str:
    global _company_counter
    if name not in _company_map:
        label = COMPANY_LABELS[_company_counter % len(COMPANY_LABELS)]
        _company_map[name] = label
        _company_counter += 1
    return _company_map[name]


def anonymize_person(name: str) -> str:
    global _person_counter
    if name not in _person_map:
        label = PERSON_LABELS[_person_counter % len(PERSON_LABELS)]
        _person_map[name] = label
        _person_counter += 1
    return _person_map[name]


def anonymize_text(text: str, extra_companies: list[str] | None = None, extra_people: list[str] | None = None) -> str:
    result = text

    all_companies = BLOCKED_COMPANIES + (extra_companies or [])
    all_people = BLOCKED_PEOPLE + (extra_people or [])

    # Replace known company names
    for company in all_companies:
        if company and len(company) > 2:
            replacement = anonymize_company(company)
            result = re.sub(re.escape(company), replacement, result, flags=re.IGNORECASE)

    # Replace known person names
    for person in all_people:
        if person and len(person) > 2:
            replacement = anonymize_person(person)
            result = re.sub(re.escape(person), replacement, result, flags=re.IGNORECASE)

    # Anonymize precise percentages → approximate
    result = re.sub(
        r'(\d+\.\d+)\s*%',
        lambda m: f"~{round(float(m.group(1)) / 5) * 5}%",
        result
    )

    # Anonymize precise currency amounts
    def anonymize_currency(m):
        value = float(m.group(1).replace(",", ""))
        if value >= 1_000_000:
            return f"~${round(value / 1_000_000)}M"
        if value >= 1_000:
            return f"~${round(value / 1_000)}K"
        return f"~${round(value / 10) * 10}"

    result = re.sub(r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)', anonymize_currency, result)

    # Strip email addresses
    result = re.sub(r'[\w.-]+@[\w.-]+\.\w+', '[email redacted]', result)

    # Strip phone numbers
    result = re.sub(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', '[phone redacted]', result)

    return result


def reset():
    global _company_map, _person_map, _company_counter, _person_counter
    _company_map = {}
    _person_map = {}
    _company_counter = 0
    _person_counter = 0
