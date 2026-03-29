"""
Digital Twin Knowledge API — Free tier, anonymized, SMILE-powered.
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from knowledge import store
from anonymizer import anonymize_text
from chat import generate_response
from resources import get_resources
from spin import advance_spin

app = FastAPI(
    title="Digital Twin Knowledge API",
    description="Free-tier API for digital twin knowledge, powered by the SMILE methodology.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    message_count: int = 0
    spin_state: dict | None = None
    spin_action: str | None = None  # "start", "answer", "skip"
    spin_value: str | None = None   # selected option value


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    cta: dict | None = None
    spin: dict | None = None  # SPIN questionnaire state


class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    tags: list
    score: float


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "knowledge_entries": len(store.entries),
        "case_studies": len(store.case_studies),
        "smile_phases": len(store.smile.get("phases", [])),
    }


@app.get("/api/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=20)):
    results = store.search(q, limit=limit)
    return {
        "query": q,
        "results": [
            {
                "id": r.id,
                "title": r.title,
                "content": anonymize_text(r.content),
                "tags": r.tags,
                "score": r.score,
            }
            for r in results
        ],
        "count": len(results),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # Handle SPIN questionnaire flow
    if req.spin_action == "start":
        spin_result = advance_spin(None, None)
        return ChatResponse(
            answer=spin_result["question"],
            sources=[],
            spin=spin_result,
        )
    elif req.spin_action == "answer" and req.spin_state is not None:
        spin_result = advance_spin(req.spin_state, req.spin_value)
        if spin_result["type"] == "spin_complete":
            return ChatResponse(
                answer="Based on your answers, here's what I'd recommend:",
                sources=[],
                spin=spin_result,
            )
        return ChatResponse(
            answer=spin_result["question"],
            sources=[],
            spin=spin_result,
        )

    # Normal chat flow
    result = await generate_response(req.question, req.message_count)
    return ChatResponse(**result)


@app.get("/api/resources")
def resources():
    return {"resources": get_resources()}


@app.get("/api/smile")
def smile_overview():
    return store.get_smile_overview()


@app.get("/api/smile/{phase_id}")
def smile_phase(phase_id: str):
    phase = store.get_phase_detail(phase_id)
    if not phase:
        return {"error": "Phase not found"}, 404
    return phase
