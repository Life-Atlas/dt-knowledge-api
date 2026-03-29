"""
Curated resources — published articles, methodology docs, and references.
"""

RESOURCES = [
    {
        "category": "SMILE Methodology",
        "items": [
            {
                "title": "Impact First, Data Last — The SMILE Approach",
                "description": "Core principle: start with outcomes, not data. How SMILE reverses the common digital twin failure mode.",
                "type": "methodology",
                "access": "free",
            },
            {
                "title": "The Six Phases of SMILE",
                "description": "From Reality Emulation to Perpetual Wisdom — the complete digital twin implementation journey.",
                "type": "methodology",
                "access": "free",
            },
            {
                "title": "Minimal Viable Twin (MVT) — Virtual First Validation",
                "description": "Apply lean methodology to digital twins. Ship value in weeks, not years.",
                "type": "methodology",
                "access": "free",
            },
        ],
    },
    {
        "category": "Smart Buildings & Energy",
        "items": [
            {
                "title": "Self-Learning Digital Twins for Municipal Schools",
                "description": "How edge-native AI optimized heating in Swedish schools — from radiator to grid level.",
                "type": "case-study",
                "access": "free",
            },
            {
                "title": "The Greenest Asset Is the One That Already Exists",
                "description": "80% of 2050's buildings exist today. How self-learning control systems cut emissions.",
                "type": "article",
                "access": "free",
            },
            {
                "title": "Democratizing Smart Buildings Through Open Systems",
                "description": "Breaking vendor lock-in with open, interoperable building platforms.",
                "type": "article",
                "access": "free",
            },
        ],
    },
    {
        "category": "Interoperability & Standards",
        "items": [
            {
                "title": "MIMs — 10 Rules That Make Digital Twins Talk to Each Other",
                "description": "Minimal Interoperability Mechanisms for cross-domain, cross-vendor digital twin ecosystems.",
                "type": "methodology",
                "access": "free",
            },
            {
                "title": "Four Layers of Interoperability",
                "description": "Technical, semantic, organizational, and legal — why most projects only address one.",
                "type": "article",
                "access": "free",
            },
            {
                "title": "Omni-Interoperability for Knowledge Transfer",
                "description": "Accelerating knowledge transfer between people, systems, and AI.",
                "type": "article",
                "access": "free",
            },
        ],
    },
    {
        "category": "Edge Computing & AI",
        "items": [
            {
                "title": "Edge-Native Is the Way — Local Control First",
                "description": "Why intelligence should be created where data is generated, not shipped to the cloud.",
                "type": "article",
                "access": "free",
            },
            {
                "title": "Explainable AI Is Easiest When Anchored in Reality",
                "description": "The AI Journey from data contextualization to explainable decision making.",
                "type": "article",
                "access": "free",
            },
            {
                "title": "Ontology Factories as Foundation for AI Factories",
                "description": "Why structured knowledge must precede AI deployment.",
                "type": "article",
                "access": "free",
            },
        ],
    },
    {
        "category": "Biological & Personal Digital Twins",
        "items": [
            {
                "title": "From Buildings to Bodies — The Biological Digital Twin",
                "description": "The same sense-model-predict-intervene pattern applied to living beings.",
                "type": "article",
                "access": "free",
            },
            {
                "title": "Your Body Deserves a Digital Twin",
                "description": "Personal digital twins for health, wellness, and longevity — edge-native, WHO-grounded.",
                "type": "article",
                "access": "free",
            },
        ],
    },
]


def get_resources() -> list[dict]:
    return RESOURCES
