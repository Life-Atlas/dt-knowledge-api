"""
SPIN questionnaire engine — Situation, Problem, Implication, Need-payoff.
Conversational qualification flow embedded in the chat widget.
"""
from products import recommend_product

# Each phase has a question and clickable options
SPIN_PHASES = [
    {
        "phase": "situation",
        "question": "Let me understand your context first. What best describes your organisation?",
        "options": [
            {"value": "startup", "label": "Startup or small company"},
            {"value": "mid_market", "label": "Mid-size organisation (50-500 people)"},
            {"value": "enterprise", "label": "Enterprise (500+ people)"},
            {"value": "public_sector", "label": "Public sector / municipality"},
            {"value": "individual", "label": "Individual / researcher"},
        ],
    },
    {
        "phase": "problem",
        "question": "What's the biggest challenge you're facing right now?",
        "options": [
            {"value": "siloed_data", "label": "Data is siloed across systems"},
            {"value": "no_visibility", "label": "No real-time visibility into operations"},
            {"value": "slow_decisions", "label": "Decision-making is too slow"},
            {"value": "vendor_lock", "label": "Locked into vendor-specific solutions"},
            {"value": "dont_know_where", "label": "Not sure where to start with digital twins"},
        ],
    },
    {
        "phase": "implication",
        "question": "What happens if this isn't solved in the next 12 months?",
        "options": [
            {"value": "cost_increase", "label": "Costs keep rising"},
            {"value": "competitive_risk", "label": "We fall behind competitors"},
            {"value": "compliance_risk", "label": "Regulatory or compliance risk"},
            {"value": "missed_opportunity", "label": "We miss a market opportunity"},
            {"value": "status_quo", "label": "Things stay the same (not urgent)"},
        ],
    },
    {
        "phase": "need",
        "question": "What would be most valuable for you right now?",
        "options": [
            {"value": "inspire_team", "label": "Inspire my team with a vision of what's possible"},
            {"value": "leadership_alignment", "label": "Get leadership aligned on a digital twin strategy"},
            {"value": "build_mvt", "label": "Build a Minimal Viable Twin for a specific use case"},
            {"value": "implementation_plan", "label": "A concrete implementation roadmap"},
            {"value": "explore", "label": "Just exploring — want to learn more first"},
        ],
    },
]

PHASE_ORDER = ["situation", "problem", "implication", "need"]


def advance_spin(spin_state: dict | None, selected_value: str | None) -> dict:
    """
    Advance the SPIN questionnaire state machine.

    Args:
        spin_state: Current state {phase_index, answers} or None to start
        selected_value: The user's selected option value, or None to start

    Returns:
        {
            "type": "spin_question" | "spin_complete",
            "phase": str,
            "question": str,           # if spin_question
            "options": list[dict],      # if spin_question
            "answers": dict,            # accumulated answers
            "phase_index": int,
            "product": dict | None,     # if spin_complete
        }
    """
    if spin_state is None:
        # Start the questionnaire
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

    # Record the answer for current phase
    current_phase = PHASE_ORDER[phase_index]
    if selected_value:
        answers[current_phase] = selected_value

    # Advance to next phase
    next_index = phase_index + 1

    if next_index >= len(SPIN_PHASES):
        # All phases complete — recommend a product
        product = recommend_product(answers)
        return {
            "type": "spin_complete",
            "phase": "complete",
            "answers": answers,
            "phase_index": next_index,
            "product": product,
        }

    # Return next question
    next_phase = SPIN_PHASES[next_index]
    return {
        "type": "spin_question",
        "phase": next_phase["phase"],
        "question": next_phase["question"],
        "options": next_phase["options"],
        "answers": answers,
        "phase_index": next_index,
    }
