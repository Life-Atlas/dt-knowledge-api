"""
SPIN Assessment Engine — 5-15 minute AI-powered strategy session.

Expanded SPIN flow:
1. Situation (2-3 questions about context)
2. Problem (2-3 questions about challenges)
3. Implication (1-2 questions about consequences)
4. Need-payoff (1-2 questions about desired outcomes)
5. Summary + personalised recommendation

Phases are adaptive — some questions only appear based on prior answers.
"""
from products import recommend_product

# ---------------------------------------------------------------------------
# Phase definitions — each phase can have multiple steps
# ---------------------------------------------------------------------------
SPIN_PHASES = [
    # ---- SITUATION: Understand the context (2-3 questions) ----
    {
        "id": "s1_org_type",
        "phase": "situation",
        "question": "Welcome to your free digital twin strategy assessment. This takes about 5-10 minutes and you'll get a personalised recommendation at the end.\n\nLet's start — what best describes your organisation?",
        "options": [
            {"value": "startup", "label": "Startup or small company (< 50 people)"},
            {"value": "mid_market", "label": "Mid-size organisation (50-500 people)"},
            {"value": "enterprise", "label": "Enterprise (500+ people)"},
            {"value": "public_sector", "label": "Public sector / municipality / government"},
            {"value": "individual", "label": "Individual / researcher / student"},
        ],
    },
    {
        "id": "s2_industry",
        "phase": "situation",
        "question": "Which industry or domain are you in?",
        "options": [
            {"value": "real_estate", "label": "Real estate / property management"},
            {"value": "construction", "label": "Construction / architecture / engineering"},
            {"value": "energy", "label": "Energy / utilities / sustainability"},
            {"value": "manufacturing", "label": "Manufacturing / industrial"},
            {"value": "healthcare", "label": "Healthcare / life sciences / wellness"},
            {"value": "smart_cities", "label": "Smart cities / urban planning / government"},
            {"value": "maritime", "label": "Maritime / shipping / logistics"},
            {"value": "other", "label": "Other"},
        ],
    },
    {
        "id": "s3_dt_maturity",
        "phase": "situation",
        "question": "How far along is your organisation with digital twins?",
        "options": [
            {"value": "curious", "label": "Haven't started — just exploring the concept"},
            {"value": "researching", "label": "Researching — comparing approaches and vendors"},
            {"value": "pilot", "label": "Running a pilot or proof of concept"},
            {"value": "deployed", "label": "Have digital twins in production"},
            {"value": "scaling", "label": "Scaling existing twins across the organisation"},
        ],
    },

    # ---- PROBLEM: Identify the core challenges (2 questions) ----
    {
        "id": "p1_challenge",
        "phase": "problem",
        "question": "Good context. Now let's dig into challenges.\n\nWhat's the single biggest problem you're trying to solve?",
        "options": [
            {"value": "siloed_data", "label": "Data is siloed — systems don't talk to each other"},
            {"value": "no_visibility", "label": "No real-time visibility into what's happening"},
            {"value": "slow_decisions", "label": "Decision-making is too slow or reactive"},
            {"value": "vendor_lock", "label": "Locked into vendor-specific solutions"},
            {"value": "cost_waste", "label": "Too much money spent on the wrong things"},
            {"value": "dont_know_where", "label": "Don't know where to start"},
        ],
    },
    {
        "id": "p2_attempted",
        "phase": "problem",
        "question": "Have you tried to solve this before?",
        "options": [
            {"value": "never", "label": "No — this is new territory for us"},
            {"value": "failed", "label": "Yes, but previous attempts didn't work"},
            {"value": "partial", "label": "Partially — we have some solutions but gaps remain"},
            {"value": "success_limited", "label": "Yes, with some success, but it doesn't scale"},
        ],
    },

    # ---- IMPLICATION: Understand the stakes (2 questions) ----
    {
        "id": "i1_consequence",
        "phase": "implication",
        "question": "Let's talk about what happens if this isn't addressed.\n\nWhat's at stake if nothing changes in the next 12 months?",
        "options": [
            {"value": "cost_increase", "label": "Costs keep rising with no way to optimise"},
            {"value": "competitive_risk", "label": "We fall behind competitors who are digitalising"},
            {"value": "compliance_risk", "label": "Regulatory or sustainability compliance risk"},
            {"value": "missed_opportunity", "label": "We miss a market or funding opportunity"},
            {"value": "talent_loss", "label": "We lose talent — people want modern tools"},
            {"value": "status_quo", "label": "Honestly, the pressure isn't urgent yet"},
        ],
    },
    {
        "id": "i2_stakeholders",
        "phase": "implication",
        "question": "Who else cares about solving this?",
        "options": [
            {"value": "just_me", "label": "Mainly me — I'm championing this internally"},
            {"value": "my_team", "label": "My team is aligned, but leadership needs convincing"},
            {"value": "leadership", "label": "Leadership is on board, we need a plan"},
            {"value": "whole_org", "label": "Organisation-wide initiative with budget"},
        ],
    },

    # ---- NEED-PAYOFF: What would success look like (2 questions) ----
    {
        "id": "n1_desired_outcome",
        "phase": "need",
        "question": "Almost there. Let's talk about what you actually want.\n\nIf you could have one outcome from working with digital twins, what would it be?",
        "options": [
            {"value": "reduce_cost", "label": "Reduce operational costs measurably"},
            {"value": "better_decisions", "label": "Make faster, data-driven decisions"},
            {"value": "sustainability", "label": "Meet sustainability or emissions targets"},
            {"value": "new_revenue", "label": "Create new revenue streams or business models"},
            {"value": "understand", "label": "Simply understand what digital twins could do for us"},
        ],
    },
    {
        "id": "n2_next_step",
        "phase": "need",
        "question": "Last question — what would be most valuable as your next step?",
        "options": [
            {"value": "inspire_team", "label": "Inspire my team with a vision of what's possible"},
            {"value": "leadership_alignment", "label": "Get leadership aligned on a strategy"},
            {"value": "build_mvt", "label": "Build a Minimal Viable Twin for a specific use case"},
            {"value": "implementation_plan", "label": "Get a concrete implementation roadmap"},
            {"value": "explore", "label": "Keep learning — I'm not ready to commit yet"},
        ],
    },
]

PHASE_ORDER = [p["id"] for p in SPIN_PHASES]

# ---------------------------------------------------------------------------
# Summary generation — personalised based on answers
# ---------------------------------------------------------------------------
INDUSTRY_NAMES = {
    "real_estate": "real estate and property management",
    "construction": "construction and engineering",
    "energy": "energy and sustainability",
    "manufacturing": "manufacturing and industrial operations",
    "healthcare": "healthcare and wellness",
    "smart_cities": "smart cities and urban planning",
    "maritime": "maritime and logistics",
    "other": "your industry",
}

MATURITY_INSIGHTS = {
    "curious": "Since you're just starting to explore digital twins, the most important thing is to **not start with data**. Start with the outcome you want to achieve, then work backwards. This is the core SMILE principle: impact first, data last.",
    "researching": "You're in the research phase — which means you're probably drowning in vendor pitches. The key question isn't 'which platform?' but 'what outcome do I want?' The right approach is vendor-agnostic and starts with your reality, not a product.",
    "pilot": "You have a pilot running — great. The critical question now is: does your twin represent **shared reality** or just one stakeholder's view? Digital twins that only serve engineers never scale. Reality must be the shared language across domains.",
    "deployed": "You have twins in production. The next frontier is **interoperability** — can your twins talk to each other and to external systems? The SMILE methodology's later phases (Continuous Intelligence, Perpetual Wisdom) are where the real compound value emerges.",
    "scaling": "You're scaling — which means you've hit the hardest part. Scaling requires ontology alignment, cross-domain interoperability, and organisational change management. This is where most programmes stall without a structured methodology.",
}

CHALLENGE_INSIGHTS = {
    "siloed_data": "Siloed data is the #1 challenge we see. The fix isn't a data platform — it's **shared reality**. When every stakeholder sees the same visual representation of reality, data alignment follows naturally.",
    "no_visibility": "Lack of visibility usually means you're making decisions based on reports about the past, not the present. A digital twin gives you a **living mirror** of reality — always current, always contextual.",
    "slow_decisions": "Slow decisions are often a symptom of missing context. When decision-makers can see the full picture — visually, in real time — speed follows. The SMILE methodology calls this 'Contextual Intelligence.'",
    "vendor_lock": "Vendor lock-in is a design choice, not an inevitability. Open, interoperable architectures using MIMs (Minimal Interoperability Mechanisms) ensure you own your data and can swap any component.",
    "cost_waste": "When you start with impact and work backwards, you eliminate 60-80% of unnecessary data collection and integration. Most cost waste comes from building things nobody asked for.",
    "dont_know_where": "Not knowing where to start is completely normal. The answer is simple: **start with reality**. Map what exists today (Phase 1 of SMILE), define what outcome you want, and build the smallest twin that delivers value.",
}


def generate_summary(answers: dict) -> str:
    """Generate a personalised assessment summary based on SPIN answers."""
    parts = []

    # Opening
    industry = INDUSTRY_NAMES.get(answers.get("s2_industry", ""), "your domain")
    parts.append(f"**Your Digital Twin Readiness Assessment**\n")

    # Situation summary
    maturity = answers.get("s3_dt_maturity", "curious")
    if maturity in MATURITY_INSIGHTS:
        parts.append(MATURITY_INSIGHTS[maturity])

    # Challenge insight
    challenge = answers.get("p1_challenge", "")
    if challenge in CHALLENGE_INSIGHTS:
        parts.append(CHALLENGE_INSIGHTS[challenge])

    # Previous attempts context
    attempted = answers.get("p2_attempted", "")
    if attempted == "failed":
        parts.append("You mentioned previous attempts didn't work. In our experience, 80% of failed digital twin projects started with data instead of impact. The SMILE methodology reverses this — and that's usually the missing piece.")
    elif attempted == "partial":
        parts.append("You have partial solutions in place. The gap is usually **interoperability** — connecting what you have into a shared reality rather than rebuilding from scratch.")

    # Stakeholder context
    stakeholders = answers.get("i2_stakeholders", "")
    if stakeholders == "my_team":
        parts.append("Since leadership still needs convincing, an **inspirational keynote** can be a powerful way to align the executive team around a shared vision before committing to implementation.")
    elif stakeholders == "leadership":
        parts.append("With leadership already on board, you're ready for a **hands-on workshop** to translate vision into a concrete implementation roadmap.")

    # Closing recommendation
    parts.append(f"\nBased on your answers, here's what I'd recommend for {industry}:")

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------
def advance_spin(spin_state: dict | None, selected_value: str | None) -> dict:
    """
    Advance the SPIN assessment state machine.

    Args:
        spin_state: Current state {phase_index, answers} or None to start
        selected_value: The user's selected option value, or None to start

    Returns:
        {
            "type": "spin_question" | "spin_complete",
            "phase": str,
            "question": str,
            "options": list[dict],
            "answers": dict,
            "phase_index": int,
            "product": dict | None,
            "summary": str | None,
        }
    """
    if spin_state is None:
        first = SPIN_PHASES[0]
        return {
            "type": "spin_question",
            "phase": first["phase"],
            "question": first["question"],
            "options": first["options"],
            "answers": {},
            "phase_index": 0,
        }

    phase_index = spin_state.get("phase_index", 0)
    answers = dict(spin_state.get("answers", {}))

    # Record the answer
    current_id = PHASE_ORDER[phase_index]
    if selected_value:
        answers[current_id] = selected_value

    # Advance
    next_index = phase_index + 1

    if next_index >= len(SPIN_PHASES):
        # Complete — generate summary and recommend product
        # Map expanded answers to the recommendation engine's expected format
        rec_answers = {
            "situation": answers.get("s1_org_type", ""),
            "problem": answers.get("p1_challenge", ""),
            "implication": answers.get("i1_consequence", ""),
            "need": answers.get("n2_next_step", ""),
        }
        product = recommend_product(rec_answers)
        summary = generate_summary(answers)

        return {
            "type": "spin_complete",
            "phase": "complete",
            "answers": answers,
            "phase_index": next_index,
            "product": product,
            "summary": summary,
        }

    next_phase = SPIN_PHASES[next_index]
    return {
        "type": "spin_question",
        "phase": next_phase["phase"],
        "question": next_phase["question"],
        "options": next_phase["options"],
        "answers": answers,
        "phase_index": next_index,
    }
