# Edu Assist — Foundation (v0.1)

This repo is being restructured from a peer-tutoring MVP into a **diagnostic assessment platform**.

## Skill areas (canonical)

1. Speaking English  
2. Writing English  
3. Mathematics  
4. Science  

Defined in:
- `backend/app/core/skills.py`
- `frontend/src/constants/skills.js`

## What works in this base version

| Layer | Status |
|-------|--------|
| Auth + student dashboard | Working (peer UI removed) |
| Legacy RAG assessment (`/assessment`) | Working — transitional |
| Topic sync after evaluation | `TopicPerformance` model + service |
| Diagnostic API (`/api/v1/diagnostic/*`) | Blueprint + session stubs |
| Peer matching API | **Disabled** (router removed) |
| PDF guides / full diagnostic battery | Not yet — see `ASSESSMENT_PLATFORM_PLAN.md` |

## Project layout

```
backend/
  app/
    core/           # skills, blueprint, config
    models/         # diagnostic.py (new), user, ...
    services/       # topic_performance_service.py (new)
    api/routes/     # diagnostic.py (new); matching.py orphaned
frontend/
  src/constants/    # skills.js
  src/services/     # diagnostic.service.js
```

## Run locally

```bash
# Backend
cd backend
pip install -r requirements.txt
# Optional: set MISTRAL_API_KEY in .env for legacy RAG grading
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Environment

Copy `.env.example` → `backend/.env`. Do not commit secrets.

## Database note

New tables (`assessment_sessions`, `topic_performances`) are created on startup.  
If you have an old `eduassess.db`, delete it once to pick up new user columns, or run:

```bash
cd backend
python scripts/reset_foundation_db.py
```

## Next phases (see ASSESSMENT_PLATFORM_PLAN.md)

1. Fixed question banks per skill area  
2. Hybrid local evaluation (Ollama + rules)  
3. Elaborative topic reports UI  
4. PDF learning guide + curated resource roadmap  
5. Delete orphaned peer-matching files  
