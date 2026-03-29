"""
Digital Twin Knowledge API — Free tier, anonymized, SMILE-powered.
"""
from fastapi import FastAPI, Query, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from knowledge import store
from anonymizer import anonymize_text
from chat import generate_response
from resources import get_resources
from spin import advance_spin, SPIN_PHASES
from ratelimit import check_rate_limit

ALLOWED_ORIGINS = [
    "https://life-atlas.github.io",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5500",
]

app = FastAPI(
    title="Digital Twin Knowledge API",
    description="Free-tier API for digital twin knowledge, powered by the SMILE methodology.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    question: str = Field("", max_length=2000)
    message_count: int = Field(0, ge=0, le=1000)
    spin_state: dict | None = None
    spin_action: str | None = Field(None, pattern=r"^(start|answer|skip)$")
    spin_value: str | None = Field(None, max_length=100)


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    cta: dict | None = None
    spin: dict | None = None


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
def search(request: Request, q: str = Query(..., min_length=1, max_length=500), limit: int = Query(5, ge=1, le=20)):
    check_rate_limit(request)
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
async def chat(request: Request, req: ChatRequest):
    check_rate_limit(request)
    # Handle SPIN questionnaire flow
    if req.spin_action == "start":
        spin_result = advance_spin(None, None)
        return ChatResponse(
            answer=spin_result["question"],
            sources=[],
            spin=spin_result,
        )
    elif req.spin_action == "answer" and req.spin_state is not None:
        # Validate spin_value against allowed options for current phase
        phase_index = req.spin_state.get("phase_index", 0)
        if 0 <= phase_index < len(SPIN_PHASES):
            allowed = [o["value"] for o in SPIN_PHASES[phase_index]["options"]]
            if req.spin_value and req.spin_value not in allowed:
                raise HTTPException(status_code=422, detail="Invalid spin option value")

        spin_result = advance_spin(req.spin_state, req.spin_value)
        if spin_result["type"] == "spin_complete":
            summary = spin_result.get("summary", "Based on your answers, here's what I'd recommend:")
            return ChatResponse(
                answer=summary,
                sources=[],
                spin=spin_result,
            )
        return ChatResponse(
            answer=spin_result["question"],
            sources=[],
            spin=spin_result,
        )

    # Normal chat flow
    if not req.question.strip():
        raise HTTPException(status_code=422, detail="Question cannot be empty")

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
        raise HTTPException(status_code=404, detail="Phase not found")
    return phase
