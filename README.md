# Edu-slab

Edu-slab is the current version of an older EduAssess-style repository: a full-stack, AI-assisted learning platform for assessments, progress tracking, peer matching, and personalized study support.

## What It Does

- Adaptive assessments for Math, Science, and English.
- AI-assisted answer evaluation and feedback.
- Chapter-level performance tracking and weakness detection.
- Peer-to-peer matching based on strengths, gaps, and location preferences.
- Personalized learning roadmaps and resource recommendations.
- Separate backend and frontend applications for API and UI concerns.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite, Pydantic, JWT auth, FAISS, Mistral/Ollama integrations.
- Frontend: React, Vite, TanStack Query, Zustand, React Router, Tailwind CSS, Recharts.

## Project Layout

- `backend/` - FastAPI application, services, migrations, and data loaders.
- `frontend/` - React/Vite user interface.
- `python_RAG/` - RAG preparation and content-processing scripts.
- `scripts/` - Utility scripts for validation and generation.

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Notes

- `.gitignore` is configured for Python, Node, IDE, and generated AI/cache artifacts.
- Some legacy files and datasets remain from the older repository structure; they can be kept or trimmed as the project is cleaned up further.

## Contributing

Create a branch, make focused changes, and open a pull request with a clear summary of the behavior changed.
