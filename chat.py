"""
Chat endpoint — RAG-lite using knowledge store + Claude Haiku.
Falls back to search-only mode if no API key is set.
"""
import os
import httpx
from knowledge import store
from anonymizer import anonymize_text

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
USE_AI = bool(ANTHROPIC_API_KEY)
BOOKING_URL = "https://cal.com/nicolaswaern"  # Update with real booking link

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


def detect_cta_trigger(query: str, message_count: int) -> dict | None:
    query_lower = query.lower()

    # Personalization trigger
    for kw in PERSONALIZATION_KEYWORDS:
        if kw in query_lower:
            return {
                "type": "consultation",
                "message": "For tailored guidance on your specific situation, Nicolas offers 1:1 strategy sessions where he can dive deep into your use case.",
                "cta_text": "Book a 1:1 Session",
                "cta_url": BOOKING_URL,
            }

    # Paid content trigger
    if store.has_paid_matches(query):
        return {
            "type": "premium",
            "message": "This topic connects to deeper case studies and implementation patterns available through direct consultation.",
            "cta_text": "Explore Premium Insights",
            "cta_url": BOOKING_URL,
        }

    # Depth trigger (after 5 messages)
    if message_count >= 5:
        return {
            "type": "depth",
            "message": "Getting value from these insights? Nicolas offers focused strategy sessions to accelerate your digital twin journey.",
            "cta_text": "Book a Strategy Session",
            "cta_url": BOOKING_URL,
        }

    return None


async def generate_response(query: str, message_count: int = 0) -> dict:
    # Search knowledge base
    results = store.search(query, limit=5)

    # Build context from search results
    context_parts = []
    sources = []
    for r in results:
        context_parts.append(f"[{r.id}] {r.title}: {r.content}")
        sources.append({"id": r.id, "title": r.title, "score": r.score})

    # Check for SMILE-specific questions
    smile_keywords = ["smile", "methodology", "phase", "phases"]
    if any(kw in query.lower() for kw in smile_keywords):
        overview = store.get_smile_overview()
        phases_text = "\n".join(
            f"Phase {p['order']}: {p['name']} — {p['description'][:150]}..."
            for p in overview["phases"]
        )
        context_parts.append(f"[SMILE Framework]\n{phases_text}")

    context = "\n\n".join(context_parts) if context_parts else "No directly relevant entries found in the knowledge base."

    # Detect CTA
    cta = detect_cta_trigger(query, message_count)

    if USE_AI:
        # Call Claude Haiku
        answer = await _call_claude(query, context)
    else:
        # Fallback: return formatted search results
        if results:
            answer = f"Here's what I found on that topic:\n\n"
            for r in results[:3]:
                answer += f"**{r.title}**\n{r.content}\n\n"
            answer += "For deeper insights, consider booking a session with Nicolas Waern."
        else:
            answer = "I don't have specific information on that topic in my knowledge base yet. Try asking about digital twins, SMILE methodology, interoperability, or edge computing."

    # Double-anonymize the response
    answer = anonymize_text(answer)

    return {
        "answer": answer,
        "sources": sources,
        "cta": cta,
    }


async def _call_claude(query: str, context: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1024,
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
            return f"I'm having trouble connecting right now. Here's a summary from the knowledge base:\n\n{context[:500]}"

        data = response.json()
        return data["content"][0]["text"]
