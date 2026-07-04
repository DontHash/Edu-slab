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
| Legacy RAG assessment (`/assessment`) | Working — loads questions from **Nepal CDC local bank** (no API key) |
| Evaluation after submit | **Professional AI via Ollama** (Nepal CDC protocol); rule-based only if Ollama is down |
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

## Database

**Active database:** `backend/data/diagnostic_platform.db` (SQLite)

The old `eduassess.db` is no longer used. Initialize a fresh database:

```bash
cd backend
python scripts/init_database.py --reset
```

This creates only the tables needed for the assessment platform (no peer-matching tables).

Tables: `users`, `schools`, `assessments`, `questions`, `student_responses`, `progress`, `resources`, `learning_materials`, `assessment_sessions`, `topic_performances`

## Next phases (see ASSESSMENT_PLATFORM_PLAN.md)

1. Fixed question banks per skill area  
2. Hybrid local evaluation (Ollama + rules)  
3. Elaborative topic reports UI  
4. PDF learning guide + curated resource roadmap  
5. Delete orphaned peer-matching files  
