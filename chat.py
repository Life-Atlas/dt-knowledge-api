"""
Chat endpoint — smart fallback using knowledge store + template synthesis.
Optionally uses Claude Haiku for richer responses when API key is available.
"""
import os
import re
import httpx
from knowledge import store
from anonymizer import anonymize_text

def _get_api_key():
    return os.getenv("ANTHROPIC_API_KEY", "")
BOOKING_URL = "https://calendly.com/futurecreation"

SYSTEM_PROMPT = """You are a digital twin knowledge assistant, powered by the SMILE methodology (Sustainable Methodology for Impact Lifecycle Enablement) created by Nicolas Waern.

You help people understand digital twins, interoperability, edge computing, and implementation strategy.

RULES — follow these exactly:
1. NEVER mention specific company names, person names, or identifying details — even if they appear in context. Use generic terms like "a Nordic municipality" or "an energy company."
2. Ground ALL answers in the provided context. Do not make up facts. If the context doesn't cover the question, say so honestly.
3. Cite which knowledge entry or concept your answer draws from when relevant.
4. Keep answers concise but substantive — 2-4 paragraphs max.
5. If the user asks for company-specific or personalized implementation advice (e.g., "what should MY company do", "how do I apply this to OUR project"), respond helpfully with general guidance, then add:
   "For tailored guidance on your specific situation, you can book a 1:1 strategy session with Nicolas Waern."
6. Be warm, knowledgeable, and practical. You represent a decade of real-world digital twin deployment experience.
7. When discussing SMILE phases, explain them clearly — users may be encountering this methodology for the first time."""

PERSONALIZATION_KEYWORDS = [
    "my company", "our company", "my organization", "our organization",
    "my project", "our project", "recommend for us", "recommend for me",
    "our situation", "my situation", "we need", "I need help with",
    "our industry", "my industry", "should we", "should I",
]


# ---------------------------------------------------------------------------
# Intent detection — figure out what the user actually wants
# ---------------------------------------------------------------------------
INTENT_PATTERNS = {
    "greeting": r"^(hi|hello|hey|good morning|good afternoon|howdy)\b",
    "what_is": r"\b(what (is|are)|define|explain|tell me about|meaning of)\b",
    "how_to": r"\b(how (do|can|should|to)|where (do|should) i start|getting started|steps to|guide)\b",
    "why": r"\b(why (is|are|do|should|does)|what.s the (point|benefit|advantage))\b",
    "compare": r"\b(difference between|compare|vs\.?|versus|better)\b",
    "example": r"\b(example|case study|real.world|show me|use case|application)\b",
    "smile": r"\b(smile|methodology|phase|phases|framework)\b",
    "opinion": r"\b(necessary|worth|important|should i|do i need|is it worth)\b",
}


def detect_intent(query: str) -> list[str]:
    """Return list of detected intents from the query."""
    q = query.lower().strip()
    intents = []
    for intent, pattern in INTENT_PATTERNS.items():
        if re.search(pattern, q):
            intents.append(intent)
    return intents or ["general"]


# ---------------------------------------------------------------------------
# Smart fallback response builder
# ---------------------------------------------------------------------------
def _extract_key_sentence(content: str) -> str:
    """Pull the most informative sentence from a knowledge entry."""
    sentences = re.split(r'(?<=[.!?])\s+', content)
    # Skip very short sentences, prefer ones with substance
    for s in sentences:
        if len(s) > 60 and not s.startswith("The pattern"):
            return s.strip()
    return sentences[0].strip() if sentences else content[:200]


def _build_smart_response(query: str, results: list, intents: list[str]) -> str:
    """Build a conversational response from search results + detected intent."""

    if not results:
        return (
            "That's an interesting question! I don't have a specific entry on that yet, "
            "but here are some topics I can help with:\n\n"
            "- **Digital twins** — what they are and how to get started\n"
            "- **SMILE methodology** — a proven 6-phase approach to implementation\n"
            "- **Interoperability** — making systems talk to each other\n"
            "- **Edge computing** — running intelligence where data lives\n\n"
            "Try asking about any of these!"
        )

    top = results[0]
    others = results[1:4]

    parts = []

    # --- Opening: context-aware, never generic ---
    if "greeting" in intents:
        parts.append("Welcome! Let me help you get oriented.\n")
    elif "what_is" in intents:
        parts.append("Great starting question — let me break it down.\n")
    elif "how_to" in intents:
        parts.append("Good thinking — here's how to approach it.\n")
    elif "why" in intents:
        parts.append("That's a key question. Here's the reasoning.\n")
    elif "opinion" in intents:
        parts.append("Good question — the short answer is: it depends on your goals. Here's the context.\n")
    elif "example" in intents:
        parts.append("Let me share a relevant example.\n")

    # --- Main answer: summarize the top result conversationally ---
    # Split content into digestible paragraphs
    content = top.content
    sentences = re.split(r'(?<=[.!?])\s+', content)

    # First 2-3 sentences as the core answer
    core = " ".join(sentences[:3])
    parts.append(f"{core}\n")

    # If there's more substance, add it as a follow-up paragraph
    if len(sentences) > 3:
        followup = " ".join(sentences[3:6])
        parts.append(f"{followup}\n")

    # --- Related insights from other results ---
    if others:
        parts.append("\n**Related insights:**\n")
        for r in others[:3]:
            key_point = _extract_key_sentence(r.content)
            # Truncate to keep it scannable
            if len(key_point) > 150:
                key_point = key_point[:147] + "..."
            parts.append(f"- **{r.title}** — {key_point}\n")

    # --- Closing: warm, not salesy ---
    parts.append("\nFeel free to ask follow-up questions — I'm here to help you navigate this.")

    return "\n".join(parts)


def detect_cta_trigger(query: str, message_count: int) -> dict | None:
    query_lower = query.lower()

    for kw in PERSONALIZATION_KEYWORDS:
        if kw in query_lower:
            return {
                "type": "spin_offer",
                "message": "I can help with that! Want to take a quick 2-minute assessment? I'll ask a few questions about your situation and recommend the best way forward.",
                "cta_text": "Start Assessment",
                "cta_action": "spin_start",
                "skip_text": "Skip — book directly",
                "skip_url": BOOKING_URL,
            }

    if store.has_paid_matches(query):
        return {
            "type": "spin_offer",
            "message": "This topic connects to deeper case studies and implementation strategies. Want a personalised recommendation?",
            "cta_text": "Take 2-Min Assessment",
            "cta_action": "spin_start",
            "skip_text": "Skip — book a session",
            "skip_url": BOOKING_URL,
        }

    if message_count >= 5:
        return {
            "type": "spin_offer",
            "message": "Getting value from these insights? I can recommend the right next step for your situation — it takes about 2 minutes.",
            "cta_text": "Find My Best Next Step",
            "cta_action": "spin_start",
            "skip_text": "Skip — book directly",
            "skip_url": BOOKING_URL,
        }

    return None


async def generate_response(query: str, message_count: int = 0) -> dict:
    results = store.search(query, limit=5)

    # Build context + sources
    context_parts = []
    sources = []
    for r in results:
        context_parts.append(f"[{r.id}] {r.title}: {r.content}")
        sources.append({"id": r.id, "title": r.title, "score": r.score})

    # SMILE-specific enrichment
    smile_keywords = ["smile", "methodology", "phase", "phases"]
    if any(kw in query.lower() for kw in smile_keywords):
        overview = store.get_smile_overview()
        phases_text = "\n".join(
            f"Phase {p['order']}: {p['name']} — {p['description'][:150]}..."
            for p in overview["phases"]
        )
        context_parts.append(f"[SMILE Framework]\n{phases_text}")

    context = "\n\n".join(context_parts) if context_parts else ""

    cta = detect_cta_trigger(query, message_count)

    # Detect user intent
    intents = detect_intent(query)

    if _get_api_key():
        answer = await _call_claude(query, context)
        answer = anonymize_text(answer)
    else:
        answer = _build_smart_response(query, results, intents)

    return {
        "answer": answer,
        "sources": sources,
        "cta": cta,
    }


async def _call_claude(query: str, context: str) -> str:
    """Call Claude Haiku with tight timeout to fit Vercel's 10s limit."""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": _get_api_key(),
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 512,
                    "system": SYSTEM_PROMPT,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Context from knowledge base:\n{context}\n\nUser question: {query}",
                        }
                    ],
                },
            )

            if response.status_code != 200:
                raise Exception(f"API returned {response.status_code}")

            data = response.json()
            return data["content"][0]["text"]
    except Exception:
        # Fallback to smart template if Claude fails or times out
        results = store.search(query, limit=5)
        intents = detect_intent(query)
        return _build_smart_response(query, results, intents)
