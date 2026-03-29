"""
Product catalog for Digital Twin consulting offerings.
Stripe Payment Links are created in the Stripe Dashboard — we just store the URLs.
"""

CALENDLY_URL = "https://calendly.com/futurecreation"

PRODUCTS = {
    "strategy": {
        "id": "strategy",
        "name": "1:1 Strategy Session",
        "description": "45-minute deep dive into your as-is situation with a readiness assessment. You receive a personalised strategy document with concrete next steps after the session.",
        "price": "EUR 500",
        "price_note": "EUR 500 discount when combined with a workshop booking",
        "link_type": "stripe",
        "url": "https://buy.stripe.com/9B6cN48bj2Rb5Rm9jnejK03",
        "cta_text": "Book Strategy Session",
        "icon": "strategy",
    },
    "workshop": {
        "id": "workshop",
        "name": "2-Hour Digital Twin Workshop",
        "description": "Hands-on workshop tailored to your situation. We map your reality, define outcomes, and build your first Minimal Viable Twin strategy together.",
        "price": "EUR 2,000",
        "price_note": "Flat rate, up to 10 participants. Includes EUR 500 discount on strategy session.",
        "link_type": "stripe",
        "url": "https://buy.stripe.com/28EbJ0gHP77rdjO1QVejK00",
        "cta_text": "Book Workshop",
        "icon": "workshop",
    },
    "lecture": {
        "id": "lecture",
        "name": "Inspirational Keynote — Where Your Future is Heading",
        "description": "1-hour keynote on the future of digital twins, AI, and interoperability — with interactive Q&A. Perfect for leadership teams and conferences.",
        "price": "From EUR 1,000",
        "price_note": "+ EUR 100/seat (up to 25 seats) for interactive Q&A",
        "link_type": "stripe",
        "url": "https://buy.stripe.com/bJe8wO8bjgI1cfK8fjejK01",
        "cta_text": "Book Keynote",
        "icon": "lecture",
    },
}

# The free AI assessment in the chat widget leads users to these products
ASSESSMENT_PRODUCT = {
    "id": "assessment",
    "name": "Free AI Strategy Assessment",
    "description": "5-10 minute AI-powered assessment. Answer a few questions about your situation and get a personalised readiness report with recommendations.",
    "price": "Free",
    "price_note": "Powered by the SMILE methodology",
    "link_type": "chat",
    "url": None,
    "cta_text": "Start Free Assessment",
    "icon": "assessment",
}


def recommend_product(answers: dict) -> dict:
    """
    Given SPIN answers, recommend the best-fit product.

    Logic:
    - Large org + strategic need → lecture (inspire leadership)
    - Specific project + implementation need → workshop (hands-on)
    - Mid-stage / needs clarity → strategy session (paid 1:1)
    - Just exploring → strategy session (entry point)
    """
    situation = answers.get("situation", "")
    need = answers.get("need", "")

    # Lecture: large orgs wanting inspiration/vision
    if situation in ("enterprise", "public_sector") and need in ("inspire_team", "leadership_alignment"):
        return PRODUCTS["lecture"]

    # Workshop: clear project, want hands-on help
    if need in ("build_mvt", "implementation_plan"):
        return PRODUCTS["workshop"]

    # Strategy session: everyone else (exploring, needs clarity, individual)
    return PRODUCTS["strategy"]
