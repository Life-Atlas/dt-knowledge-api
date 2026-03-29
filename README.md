# DT Knowledge API

FastAPI backend for the Digital Twin Course chat widget. Powers knowledge search, SPIN qualification questionnaire, and product recommendations.

## Quick Start

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/search?q=...` | Knowledge base search |
| POST | `/api/chat` | Chat + SPIN questionnaire |
| GET | `/api/resources` | Curated resource list |
| GET | `/api/smile` | SMILE methodology overview |
| GET | `/api/smile/{phase_id}` | SMILE phase detail |

## Tests

```bash
pip install pytest httpx
python -m pytest tests/ -v
```

## Deployment

Deployed to Vercel via `vercel --prod`. See `vercel.json` for config.

## Environment Variables

See `.env.example`. The API works without any env vars (fallback mode).
