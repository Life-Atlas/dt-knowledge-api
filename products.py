"""
Product catalog for Digital Twin consulting offerings.
Stripe Payment Links are created in the Stripe Dashboard — we just store the URLs.
"""

CALENDLY_URL = "https://calendly.com/futurecreation"

PRODUCTS = {
    "workshop": {
        "id": "workshop",
        "name": "2-Hour Digital Twin Workshop",
        "description": "Hands-on workshop tailored to your situation. We map your reality, define outcomes, and build your first Minimal Viable Twin strategy together.",
        "price": "EUR 2,500",
        "price_note": "Flat rate, up to 10 participants",
        "link_type": "stripe",
        "url": CALENDLY_URL,  # Placeholder until Stripe Payment Link is created
        "cta_text": "Book Workshop",
        "icon": "workshop",
    },
    "lecture": {
        "id": "lecture",
        "name": "Inspirational Keynote",
        "description": "1-hour keynote on the future of digital twins, AI, and interoperability — with interactive Q&A. Perfect for leadership teams and conferences.",
        "price": "From EUR 10,000",
        "price_note": "+ EUR 100/seat (up to 25 seats) for interactive Q&A",
        "link_type": "stripe",
        "url": CALENDLY_URL,  # Placeholder until Stripe Payment Link is created
        "cta_text": "Book Keynote",
        "icon": "lecture",
    },
    "strategy": {
        "id": "strategy",
        "name": "1:1 Strategy Session",
        "description": "Free initial session to explore your digital twin challenges. Get personalised guidance on where to start and how to avoid common pitfalls.",
        "price": "Free",
        "price_note": "30 min, no commitment",
        "link_type": "calendly",
        "url": CALENDLY_URL,
        "cta_text": "Book Free Session",
        "icon": "strategy",
    },
}


def recommend_product(answers: dict) -> dict:
    """
    Given SPIN answers, recommend the best-fit product.

    Logic:
    - Large org + strategic need → lecture (inspire leadership)
    - Specific project + implementation need → workshop (hands-on)
    - Exploring / early stage / individual → strategy session (free)
    """
    situation = answers.get("situation", "")
    need = answers.get("need", "")

    # Lecture: large orgs wanting inspiration/vision
    if situation in ("enterprise", "public_sector") and need in ("inspire_team", "leadership_alignment"):
        return PRODUCTS["lecture"]

    # Workshop: clear project, want hands-on help
    if need in ("build_mvt", "implementation_plan"):
        return PRODUCTS["workshop"]

    # Strategy: exploring, early stage, or individual
    return PRODUCTS["strategy"]
