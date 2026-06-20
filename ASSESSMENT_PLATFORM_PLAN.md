# Edu Assist Refactor Plan — Standardized Assessment Platform

**Document version:** 1.0  
**Date:** June 20, 2026  
**Scope:** Convert Edu Assist from a peer-learning MVP into a focused **initial diagnostic assessment platform** with topic reports, downloadable learning guides, and a resource roadmap UI.

**Constraints preserved:**
- Existing website (React + FastAPI)
- Existing visual theme and palette (cream `#DDD0C8`, charcoal `#323232`, sand surfaces — no redesign)
- Local GPU: **RTX 2050** (~8 GB VRAM class — plan assumes quantized local models)

---

## 1. Vision & Success Criteria

### What we are building

A student signs up, completes a **standardized initial diagnostic battery** across four skill areas:

| # | Skill area | What it measures |
|---|------------|------------------|
| 1 | **Speaking English** | Pronunciation, fluency, grammar in speech, vocabulary in context |
| 2 | **Writing English** | Grammar, structure, coherence, spelling, vocabulary in written form |
| 3 | **Mathematics** | Topic-level understanding (e.g. Geometry, Algebra, Statistics) |
| 4 | **Science** | Topic-level understanding (e.g. Physics, Chemistry, Biology branches) |

After completion, the student receives:

1. **Elaborative topic-wise report** — strengths and weaknesses per topic, with reasoning (e.g. *"Geometry: you lost marks on angle reasoning and proof-style steps, but did well on area/perimeter calculations"*).
2. **Downloadable PDF learning guide** — reusable template, includes prerequisites + study sequence + practice focus.
3. **Interactive roadmap UI** — same plan rendered in-app with embedded/linked **free resources** (YouTube, Khan Academy, BBC Bitesize, etc.).

### What we are removing

- **All peer matching** — Gale–Shapley matching, tutor/learner cards, location/GPS matching, chat, help requests, fit-to-teach logic, teacher match creation.

### Definition of done

- [ ] Student can complete all 4 standardized assessments in one guided flow.
- [ ] Each subject produces a structured topic report stored in DB (not only JSON files).
- [ ] Report page shows per-topic strengths, weaknesses, and detailed reasoning.
- [ ] PDF learning guide downloads from a reusable Jinja2/HTML template.
- [ ] Roadmap UI shows curated free resources per weak topic with prerequisites.
- [ ] No peer-matching code paths remain (backend routes, models, frontend UI).
- [ ] AI stack runs efficiently on RTX 2050 (local inference for grading; no mandatory cloud API).
- [ ] UI palette unchanged; navigation simplified for assessment-only workflow.

---

## 2. Current State (Baseline)

### Active assessment path today

```
RAGAssessmentPage → POST /api/v1/rag/generate-questions → Mistral (cloud)
                 → POST /api/v1/rag/submit-assessment
                 → evaluation_service.py (Mistral cloud)
                 → JSON files in backend/assessments/{user_id}/
                 → matching_service.update_student_chapter_performances()  ← REMOVE
                 → AssessmentEvaluationPage (basic chapter view)
```

### Problems with current approach

| Problem | Impact |
|---------|--------|
| Questions generated ad hoc via RAG + Mistral | Not standardized; different students get different difficulty/count |
| English treated as one subject | Cannot separate **speaking** vs **writing** |
| Evaluation via cloud Mistral API | Cost, latency, inconsistency, API key in config |
| Results in flat JSON files | Hard to query, no durable topic history |
| Weakness data tied to `StudentChapterPerformance` (matching model) | Blocks clean removal of peer matching |
| No PDF export | Missing deliverable |
| Resource links AI-hallucinated | Unvalidated URLs in learning materials |
| Peer matching embedded in dashboard + post-eval hooks | Scope creep |

### Existing assets to reuse

| Asset | Path | Reuse strategy |
|-------|------|----------------|
| Curriculum JSON (Math/Science grades 6–10) | `python_RAG/data/MathematicsGrade*.json`, `ScienceGrade*.json` | Source for **fixed question banks** per topic |
| English JSONL corpus | `python_RAG/data/*_formatted.jsonl` | Source for **writing** exercises; speaking needs new content |
| Evaluation JSON schema (`chapter_analysis`) | `evaluation_service.py` | Extend to **topic report** schema |
| Learning roadmap UI | `frontend/src/components/student/LearningRoadmap.jsx` | Enhance with validated resource links |
| Auth, layout, palette | `DashboardLayout`, `Sidebar`, common components | Keep as-is structurally |
| Learning materials service | `Learning_materials.py` | Rewire weakness source; add PDF generation |

---

## 3. Target Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React 19 + Vite)                       │
├─────────────────────────────────────────────────────────────────────────┤
│  Onboarding → Diagnostic Battery (4 steps) → Topic Report → Roadmap    │
│                     ↓                              ↓            ↓        │
│              Assessment UI                   Report Page    PDF Download │
│              (per skill area)                (elaborative)  Resource UI  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ REST /api/v1
┌──────────────────────────────▼──────────────────────────────────────────┐
│                         BACKEND (FastAPI)                                │
├─────────────────────────────────────────────────────────────────────────┤
│  assessment_orchestrator.py   — fixed test structure, session state      │
│  question_bank_service.py     — curated questions from JSON banks        │
│  evaluation_engine.py         — hybrid: rules + local LLM (Ollama)       │
│  topic_report_service.py      — build elaborative per-topic reports      │
│  resource_curator_service.py  — validated free-resource lookup           │
│  pdf_guide_service.py         — HTML template → PDF (WeasyPrint)         │
│  learning_roadmap_service.py  — prerequisites + steps + resources        │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
   SQLite/Postgres      Ollama (local GPU)     Static resource index
   (sessions, reports)  Qwen2.5 / Phi-3        (YAML/JSON, curated URLs)
```

---

## 4. Standardized Initial Assessment Design

### 4.1 Four skill areas (not three subjects + social)

Replace the current `maths | science | english` triad with:

```python
SKILL_AREAS = [
    "speaking_english",
    "writing_english",
    "mathematics",
    "science",
]
```

Update `User` model levels accordingly:

| Old column | New column |
|------------|------------|
| `math_level` | `mathematics_level` (or keep `math_level`) |
| `science_level` | `science_level` |
| `english_level` | Split → `speaking_english_level`, `writing_english_level` |
| `fit_to_teach_level` | **Remove** |
| `location`, `latitude`, `longitude` | **Remove** |

### 4.2 Standardized test blueprint (initial diagnostic)

Each skill area uses a **fixed blueprint** so every student gets the same structure (questions may rotate from a pool, but counts and topics are fixed).

#### Speaking English (~15–20 min)

| Section | Format | Count | Evaluation method |
|---------|--------|-------|-------------------|
| Read-aloud | Student records audio (Web MediaRecorder) | 2 prompts | Local Whisper transcription + rubric scoring |
| Picture description | Audio response to image prompt | 1 | Transcript + LLM rubric |
| Short spoken answer | Audio Q&A | 3 | Transcript + LLM rubric |
| Multiple choice (listening) | Audio clip + MCQ | 5 | Deterministic |

**Topics tagged:** pronunciation, fluency, grammar-in-speech, vocabulary, comprehension.

#### Writing English (~25–30 min)

| Section | Format | Count | Evaluation method |
|---------|--------|-------|-------------------|
| Grammar correction | Fix sentence errors | 5 | Rule-based + LLM |
| Sentence completion | Fill/transform | 5 | Rule-based |
| Paragraph writing | 1 prompt (120–150 words) | 1 | Local LLM rubric |
| Essay / letter | 1 prompt (200–250 words) | 1 | Local LLM rubric |

**Topics tagged:** grammar, punctuation, vocabulary, structure, coherence — sourced from existing `*_formatted.jsonl` where possible.

#### Mathematics (~30–35 min)

| Section | Format | Count | Evaluation method |
|---------|--------|-------|-------------------|
| MCQ per topic | Fixed topics from grade JSON | 3–4 per topic | Deterministic |
| Short answer | Show working / numeric answer | 2 per topic | Rule-based + LLM for method |

**Topics (Grade 10 example from existing data):** Algebra, Geometry, Trigonometry, Statistics, Number Systems — pulled from `MathematicsGrade10.json` chapter list.

#### Science (~30–35 min)

Same pattern as mathematics using `ScienceGrade*.json` chapters.

### 4.3 Assessment session model

New DB entity to replace file-only storage:

```
AssessmentSession
├── id, student_id, status (not_started | in_progress | completed)
├── started_at, completed_at
├── current_skill_area
└── skill_results[] → AssessmentSkillResult

AssessmentSkillResult
├── skill_area (enum)
├── assessment_session_id
├── raw_answers (JSON)
├── evaluation_id → AssessmentEvaluation

AssessmentEvaluation
├── skill_area
├── overall_score (0–100)
├── overall_level (grade estimate)
├── topic_analysis (JSON) — see §5
└── created_at

TopicPerformance  (normalized for queries & roadmap)
├── student_id, skill_area, topic_name
├── score (0–10), accuracy_pct, weakness_level
├── strengths (JSON array of strings)
├── weaknesses (JSON array of strings)
├── reasoning (text — elaborative explanation)
└── assessed_at
```

---

## 5. Elaborative Topic-Wise Reporting

### 5.1 Target report schema

Extend current `chapter_analysis` into a richer **topic report**:

```json
{
  "skill_area": "mathematics",
  "overall_score": 72,
  "overall_summary": "You show solid arithmetic fluency but geometry reasoning needs work.",
  "topics": {
    "Geometry": {
      "score_out_of_10": 4.5,
      "accuracy_percentage": 45,
      "weakness_level": "severe",
      "performance_label": "Needs focused practice",
      "strengths": [
        "Correctly calculated areas of rectangles and triangles",
        "Good recall of basic angle types"
      ],
      "weaknesses": [
        "Struggled with angle relationships in parallel lines",
        "Did not justify steps in proof-style questions"
      ],
      "reasoning": "In Q3 and Q7 you identified shapes correctly but applied the wrong angle rule when lines were parallel. Q9 was fully correct — you handled perimeter well.",
      "question_breakdown": [
        {
          "question_id": "geo_q3",
          "your_answer": "...",
          "expected_approach": "...",
          "verdict": "incorrect",
          "mistake_type": "conceptual — alternate interior angles"
        }
      ]
    }
  }
}
```

### 5.2 Evaluation engine (replace pure Mistral cloud)

**Hybrid approach** — faster, cheaper, more consistent on RTX 2050:

| Answer type | Engine | Model / tool |
|-------------|--------|--------------|
| MCQ, True/False | Deterministic string match | Python — no GPU |
| Numeric / short math | SymPy + tolerance compare | Python — no GPU |
| Grammar MCQ / fill-blank | Rule patterns + fuzzy match | Python + `rapidfuzz` |
| Speaking (audio) | Whisper → transcript → rubric LLM | `whisper-small` or `distil-whisper` local |
| Writing essays | Rubric-scored LLM | Ollama: `qwen2.5:7b-instruct-q4_K_M` |
| Science short answer | LLM with strict JSON output | Same local model |

**Why this beats current Mistral-only approach:**

- MCQ/ numeric scoring becomes **deterministic** (eliminates LLM hallucination on objective items).
- Local **Qwen2.5 7B Q4** fits ~5 GB VRAM — leaves headroom on RTX 2050 for Whisper batch jobs.
- **Ollama** provides OpenAI-compatible API — minimal code change from current Mistral client.
- Fallback: if GPU unavailable, use `phi3:mini` (3.8B) for lighter machines.

**Remove:**
- FAISS RAG for question generation (replace with fixed question banks).
- Cloud Mistral dependency for core grading (optional fallback only).

### 5.3 Report UI pages

| Page | Route | Purpose |
|------|-------|---------|
| `DiagnosticResultsPage` | `/results` | Overview of all 4 skill areas |
| `TopicReportPage` | `/results/:skillArea` | Full elaborative topic breakdown |
| Keep/refactor | `/assessment-evaluation/:id` | Redirect or merge into above |

**UI sections per topic card:**
- Score badge + weakness level (existing color tokens)
- "What you did well" (green-tinted list)
- "What needs work" (amber/red list)
- "Detailed analysis" (reasoning paragraph)
- Expandable per-question breakdown

---

## 6. Learning Guide (PDF) + Resource Roadmap UI

### 6.1 PDF learning guide

**Template approach** — single reusable Jinja2 HTML template rendered to PDF.

```
backend/app/templates/learning_guide/
├── base.html              # Shared layout, logo, palette colors inline
├── cover.html             # Student name, date, skill area summary
├── topic_section.html     # Per-topic: prerequisites, steps, practice
└── styles.css             # Print-friendly; matches #DDD0C8 / #323232 theme
```

**Service:** `pdf_guide_service.py` using **WeasyPrint** (or ReportLab if WeasyPrint install is problematic on Windows).

**PDF contents per weak topic:**
1. Topic name + current score
2. **Prerequisites** (concepts you should know first) — with links
3. **Learning sequence** (ordered steps, time estimates)
4. **Practice focus** (specific sub-skills from report weaknesses)
5. **Recommended free resources** (validated URLs only)
6. **Checkpoint questions** (3–5 from question bank for self-test)

**API:**
- `POST /api/v1/learning-guides/generate` — builds guide from latest `TopicPerformance`
- `GET /api/v1/learning-guides/{id}/pdf` — download PDF
- `GET /api/v1/learning-guides/{id}/preview` — HTML preview in browser

### 6.2 Resource roadmap UI

Enhance existing `LearningRoadmap.jsx` — do not rebuild from scratch.

**Resource curation strategy (no hallucinated URLs):**

Maintain a **curated static index** instead of asking the LLM to invent links:

```
backend/data/resource_index.yaml
```

Example entry:

```yaml
mathematics:
  Geometry:
    prerequisites:
      - topic: "Basic Angles"
        resources:
          - type: video
            title: "Angles - Introduction"
            url: "https://www.youtube.com/watch?v=..."
            provider: youtube
          - type: article
            title: "Angles"
            url: "https://www.khanacademy.org/math/..."
            provider: khan_academy
    weak_area_resources:
      parallel_lines:
        - type: video
          title: "..."
          url: "..."
```

**LLM role:** Select and rank from the curated index based on weakness tags — **never generate URLs**.

**Roadmap UI features:**
- Timeline/stepper view per topic (existing expandable cards → upgrade)
- Resource cards with provider icons (YouTube, Khan Academy, BBC Bitesize)
- Prerequisites shown as nested accordion above main topic
- "Download PDF guide" button per skill area
- Filter: show only weak / moderate topics (default)

---

## 7. Peer Matching — Complete Removal Checklist

### 7.1 Backend — delete

| File | Action |
|------|--------|
| `backend/app/api/routes/matching.py` | Delete |
| `backend/app/services/matching_service.py` | Delete |
| `backend/app/models/matching.py` | Delete |
| `backend/app/schemas/matching.py` | Delete |
| `backend/migrations/add_peer_matching.py` | Delete |
| `backend/migrations/add_communication_features.py` | Delete |
| `backend/migrations/add_meeting_types_and_location.py` | Delete |
| `backend/check_matching.py`, `populate_performance.py`, `force_update_performance.py`, `test_subject_match.py`, `fix_fit_to_teach.py`, `downgrade_fit_to_teach.py` | Delete |

### 7.2 Backend — modify

| File | Change |
|------|--------|
| `backend/app/api/api.py` | Remove `matching.router` |
| `backend/app/models/__init__.py` | Remove matching imports |
| `backend/app/api/routes/rag_questions.py` | Remove `update_student_chapter_performances()` calls; remove fit-to-teach updates |
| `backend/app/models/user.py` | Remove peer-related columns |
| `backend/app/services/Learning_materials.py` | Read weaknesses from `TopicPerformance`, not `StudentChapterPerformance` |

### 7.3 Frontend — delete

| File | Action |
|------|--------|
| `frontend/src/pages/student/PeerMatchingPage.jsx` | Delete |
| `frontend/src/pages/teacher/CreateMatchesPage.jsx` | Delete |
| `frontend/src/components/peers/*` | Delete folder |
| `frontend/src/components/matching/CommunicationPanel.jsx` | Delete |
| `frontend/src/components/map/LocationMap.jsx`, `UsageMap.jsx` | Delete |
| `frontend/src/services/matching.service.js` | Delete |
| `frontend/src/services/communication.service.js` | Delete |

### 7.4 Frontend — modify

| File | Change |
|------|--------|
| `frontend/src/components/student/StudentDashboard.jsx` | Remove all peer sections; show diagnostic progress + latest reports + roadmap CTA |
| `frontend/src/pages/student/AssessmentEvaluationPage.jsx` | Remove fit-to-teach alert; link to roadmap |
| `frontend/index.html` | Title: "Edu Assist" (not "Peer Learning Platform") |

### 7.5 Database migration

New Alembic migration:
- Drop tables: `peer_matches`, `tutoring_sessions`, `student_chapter_performance`, `help_requests`, `help_offers`, `chat_messages`, `shared_resources`
- Drop columns on `users`: `fit_to_teach_level`, `location`, `latitude`, `longitude`
- Add columns: `speaking_english_level`, `writing_english_level`
- Create tables: `assessment_sessions`, `assessment_skill_results`, `assessment_evaluations`, `topic_performances`, `learning_guides`

---

## 8. AI / ML Stack Recommendation (RTX 2050)

### 8.1 Recommended stack

| Task | Recommendation | VRAM | Notes |
|------|----------------|------|-------|
| Local LLM inference | **Ollama** + `qwen2.5:7b-instruct-q4_K_M` | ~5 GB | Best quality/size ratio for grading essays & explanations |
| Lightweight fallback | `phi3:mini` via Ollama | ~2.5 GB | If simultaneous Whisper + LLM exceeds VRAM |
| Speech-to-text | **faster-whisper** (`small` or `distil-small.en`) | ~1–2 GB | Run sequentially with LLM, not parallel |
| Embeddings (optional) | `nomic-embed-text` via Ollama | ~0.5 GB | Only if semantic similarity needed later |
| Objective grading | Python (SymPy, regex, rapidfuzz) | 0 | Always prefer deterministic when possible |
| PDF generation | WeasyPrint | CPU | No GPU needed |

### 8.2 What to remove / deprioritize

| Current | Replace with |
|---------|--------------|
| Mistral cloud API (primary) | Ollama local (primary); Mistral optional fallback |
| FAISS RAG question generation | Fixed question banks from JSON |
| `mistral-embed` cloud embeddings | Not needed for v1 |
| scikit-learn in hot path | Remove unless used elsewhere |

### 8.3 Inference workflow (VRAM-safe)

```
For each student submission:
  1. Grade all MCQ/numeric items in Python     (no GPU)
  2. If speaking section present:
       a. Transcribe audio with faster-whisper  (GPU, then unload)
  3. Batch open-ended items → single LLM call    (GPU, JSON mode)
  4. Build topic report from structured output (CPU)
```

**Do not** run Whisper and 7B LLM simultaneously on 8 GB VRAM.

### 8.4 New backend dependencies

```txt
# Add
ollama>=0.4.0            # Python client (talks to local Ollama daemon)
faster-whisper>=1.0.0
sympy>=1.12
rapidfuzz>=3.0
weasyprint>=62.0
jinja2>=3.1
pyyaml>=6.0

# Optional remove later
# mistralai
# faiss-cpu
```

**Dev setup note:** Install [Ollama](https://ollama.com) separately; pull models once:
```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull whisper  # or use faster-whisper model files directly
```

---

## 9. Frontend Restructure (Theme Preserved)

### 9.1 Navigation (simplified)

| Sidebar item | Route | Status |
|--------------|-------|--------|
| Dashboard | `/dashboard` | Modify — assessment-focused |
| Diagnostic Test | `/diagnostic` | **New** — 4-step battery |
| My Results | `/results` | **New** — topic reports |
| Learning Roadmap | `/roadmap` | Rename from Resources |
| ~~Assessment~~ | `/assessment` | Merge into `/diagnostic` |

Remove from sidebar: any peer/matching references.

### 9.2 Palette — centralize without changing colors

Add to `tailwind.config.js` (values unchanged):

```js
theme: {
  extend: {
    colors: {
      cream: { DEFAULT: '#DDD0C8', light: '#F5EDE5', sidebar: '#E8DDD3' },
      sand: { border: '#C9BDB3' },
      charcoal: { DEFAULT: '#323232', muted: '#5A5A5A' },
      accent: { DEFAULT: '#8B7355' },
      weakness: { severe: '#7C2D12' },
    },
  },
},
```

Gradually replace inline `style={{ color: '#323232' }}` with `text-charcoal` — **same hex, cleaner code**.

### 9.3 New / modified pages

| File | Action |
|------|--------|
| `pages/student/DiagnosticBatteryPage.jsx` | **Create** — 4-step wizard with progress stepper |
| `pages/student/DiagnosticResultsPage.jsx` | **Create** — all skill areas summary |
| `pages/student/TopicReportPage.jsx` | **Create** — elaborative per-skill report |
| `pages/student/RoadmapPage.jsx` | **Create** (or rename ResourcesPage) — resource UI + PDF button |
| `pages/student/RAGAssessmentPage.jsx` | **Replace** by DiagnosticBatteryPage |
| `components/assessment/AudioRecorder.jsx` | **Create** — speaking section |
| `components/assessment/DiagnosticStepper.jsx` | **Create** — progress across 4 areas |
| `components/student/LearningGuideDownload.jsx` | **Create** — PDF trigger + status |
| `components/student/ResourceCard.jsx` | **Create** — YouTube/Khan/embed link card |
| `services/diagnostic.service.js` | **Create** — new API client |
| `services/learningGuide.service.js` | **Create** — PDF + roadmap API |

### 9.4 Role simplification (optional phase 2)

For v1, **student flow is primary**. Teacher/admin dashboards can remain but deprioritized:
- Remove teacher match creation (deleted)
- Teacher view: see student diagnostic reports (future)

---

## 10. Backend API Restructure

### 10.1 New route modules

| Router | Prefix | Endpoints |
|--------|--------|-----------|
| `diagnostic.py` | `/diagnostic` | `POST /session/start`, `GET /session/current`, `POST /session/{id}/skill/{area}/submit`, `GET /session/{id}/status` |
| `topic_reports.py` | `/reports` | `GET /`, `GET /{skill_area}`, `GET /{skill_area}/topics/{topic}` |
| `learning_guides.py` | `/learning-guides` | `POST /generate`, `GET /{id}`, `GET /{id}/pdf`, `GET /{id}/resources` |

### 10.2 Modify existing

| Router | Change |
|--------|--------|
| `rag_questions.py` | **Deprecate** — redirect to `/diagnostic` or remove after migration |
| `learning_materials.py` | Merge into `learning_guides.py` or alias |
| `users.py` | Remove `/locations`; update profile schema |

### 10.3 New services

| Service file | Responsibility |
|--------------|----------------|
| `assessment_orchestrator.py` | Session lifecycle, blueprint enforcement |
| `question_bank_service.py` | Load & serve fixed questions from JSON |
| `evaluation_engine.py` | Hybrid grading pipeline |
| `topic_report_service.py` | Aggregate scores → elaborative report |
| `resource_curator_service.py` | Match weaknesses to curated resource index |
| `pdf_guide_service.py` | Jinja2 → PDF |
| `ollama_client.py` | Wrapper for local LLM calls with JSON mode |
| `speech_service.py` | Audio upload, Whisper transcription |

### 10.4 Shared config

```
backend/app/core/subjects.py     # SKILL_AREAS enum, blueprint constants
backend/app/core/assessment_blueprint.py  # Question counts, time limits
backend/data/question_banks/     # Organized copies/symlinks to python_RAG/data
backend/data/resource_index.yaml # Curated free resources
```

---

## 11. Content / Data Work Required

### 11.1 Question banks to create or organize

| Skill area | Source | Gap |
|------------|--------|-----|
| Mathematics | `MathematicsGrade6–10.json` | Organize into `question_banks/mathematics/` with stable IDs |
| Science | `ScienceGrade6–10.json` | Same |
| Writing English | `*_formatted.jsonl` | Convert to structured JSON with topic tags |
| Speaking English | **None exists** | **Create new bank** — prompts, MCQ listening clips, picture prompts |

### 11.2 Speaking English content (new)

Minimum viable bank for v1:
- 10 read-aloud passages (grade 6–10 variants)
- 5 picture description prompts
- 15 short-answer speaking prompts
- 20 listening MCQs (store audio files in `backend/data/audio/` or use TTS-generated clips)

### 11.3 Resource index (curated)

Build `resource_index.yaml` incrementally:
- Phase 1: Top 3 weak topics per skill area (manual curation)
- Phase 2: Full topic coverage for grades 6–10

---

## 12. Implementation Phases

### Phase 0 — Foundation (Week 1)

- [ ] Add this plan's DB models + Alembic migration
- [ ] Create `subjects.py`, `assessment_blueprint.py`
- [ ] Set up Ollama + faster-whisper locally; add `ollama_client.py`
- [ ] Centralize Tailwind palette tokens (no visual change)
- [ ] Remove peer matching backend routes (feature flag off first)

**Deliverable:** App runs without matching; new empty models exist.

### Phase 1 — Question banks & diagnostic session (Week 2)

- [ ] Build `question_bank_service.py`
- [ ] Organize math/science JSON into stable question IDs
- [ ] Convert writing English JSONL → structured bank
- [ ] Create speaking English starter bank
- [ ] Implement `assessment_orchestrator.py` + `/diagnostic` API
- [ ] Build `DiagnosticBatteryPage.jsx` + stepper UI

**Deliverable:** Student can take fixed-structure tests for all 4 areas.

### Phase 2 — Hybrid evaluation & topic reports (Week 3)

- [ ] Implement `evaluation_engine.py` (deterministic + Ollama)
- [ ] Add `speech_service.py` + `AudioRecorder.jsx`
- [ ] Implement `topic_report_service.py` + elaborative schema
- [ ] Build `TopicReportPage.jsx` + `DiagnosticResultsPage.jsx`
- [ ] Persist to `TopicPerformance` table

**Deliverable:** Elaborative topic reports with strengths, weaknesses, reasoning.

### Phase 3 — Learning guide & roadmap (Week 4)

- [ ] Build `resource_index.yaml` (initial curated set)
- [ ] Implement `resource_curator_service.py`
- [ ] Create PDF Jinja2 templates matching existing palette
- [ ] Implement `pdf_guide_service.py` + download endpoint
- [ ] Upgrade `LearningRoadmap.jsx` → resource cards with real links
- [ ] Build `RoadmapPage.jsx` + PDF download button

**Deliverable:** Downloadable PDF + in-app roadmap with free resources.

### Phase 4 — Cleanup & deprecation (Week 5)

- [ ] Remove `matching_service`, models, frontend peer UI
- [ ] Deprecate `/rag/*` endpoints; remove FAISS/Mistral from hot path
- [ ] Strip `StudentDashboard.jsx` peer sections
- [ ] Remove `fit_to_teach` from evaluation page alerts
- [ ] Update README + remove outdated peer docs
- [ ] Migration: drop peer tables

**Deliverable:** Clean assessment-only codebase.

### Phase 5 — Polish & testing (Week 6)

- [ ] End-to-end test: register → diagnostic → report → PDF → roadmap
- [ ] Load test Ollama grading pipeline (sequential GPU usage)
- [ ] Validate all resource URLs (scripted link checker)
- [ ] Accessibility pass on new pages
- [ ] Error states: GPU unavailable, partial session resume

**Deliverable:** Production-ready pilot.

---

## 13. File Action Matrix (Quick Reference)

### Create

```
backend/app/models/assessment_session.py
backend/app/models/topic_performance.py
backend/app/models/learning_guide.py
backend/app/schemas/diagnostic.py
backend/app/schemas/topic_report.py
backend/app/schemas/learning_guide.py
backend/app/services/assessment_orchestrator.py
backend/app/services/question_bank_service.py
backend/app/services/evaluation_engine.py
backend/app/services/topic_report_service.py
backend/app/services/resource_curator_service.py
backend/app/services/pdf_guide_service.py
backend/app/services/ollama_client.py
backend/app/services/speech_service.py
backend/app/api/routes/diagnostic.py
backend/app/api/routes/topic_reports.py
backend/app/api/routes/learning_guides.py
backend/app/core/subjects.py
backend/app/core/assessment_blueprint.py
backend/app/templates/learning_guide/*.html
backend/data/resource_index.yaml
backend/data/question_banks/speaking_english/
frontend/src/pages/student/DiagnosticBatteryPage.jsx
frontend/src/pages/student/DiagnosticResultsPage.jsx
frontend/src/pages/student/TopicReportPage.jsx
frontend/src/pages/student/RoadmapPage.jsx
frontend/src/components/assessment/AudioRecorder.jsx
frontend/src/components/assessment/DiagnosticStepper.jsx
frontend/src/components/student/LearningGuideDownload.jsx
frontend/src/components/student/ResourceCard.jsx
frontend/src/services/diagnostic.service.js
frontend/src/services/learningGuide.service.js
alembic/versions/xxxx_assessment_platform_refactor.py
```

### Delete

```
backend/app/api/routes/matching.py
backend/app/services/matching_service.py
backend/app/models/matching.py
backend/app/schemas/matching.py
frontend/src/pages/student/PeerMatchingPage.jsx
frontend/src/pages/teacher/CreateMatchesPage.jsx
frontend/src/components/peers/
frontend/src/components/matching/
frontend/src/components/map/
frontend/src/services/matching.service.js
frontend/src/services/communication.service.js
(+ debug scripts listed in §7.1)
```

### Modify

```
backend/app/api/api.py
backend/app/models/user.py
backend/app/models/__init__.py
backend/app/services/Learning_materials.py  → merge or replace
backend/app/api/routes/rag_questions.py     → deprecate
frontend/src/App.jsx
frontend/src/components/layout/Sidebar.jsx
frontend/src/components/student/StudentDashboard.jsx
frontend/src/components/student/LearningRoadmap.jsx
frontend/src/pages/student/AssessmentEvaluationPage.jsx
frontend/tailwind.config.js
frontend/index.html
backend/requirements.txt
backend/app/core/config.py  → add OLLAMA_BASE_URL, remove hardcoded API key
README.md
```

---

## 14. Testing Plan

| Test | Method |
|------|--------|
| Blueprint consistency | Same question counts for every student session |
| MCQ grading accuracy | Unit tests with known answers |
| Math numeric tolerance | SymPy tests for equivalent expressions |
| LLM JSON output | Schema validation on Ollama responses |
| Speaking pipeline | Upload sample audio → transcript → score |
| Topic report completeness | Every attempted topic has strengths + weaknesses |
| PDF generation | Render test report; verify palette colors in output |
| Resource links | CI script: HTTP HEAD check on `resource_index.yaml` |
| Peer matching removed | Grep + integration test: `/matching` returns 404 |
| Session resume | Kill browser mid-diagnostic → resume from last skill area |
| GPU memory | Monitor VRAM during sequential Whisper → LLM run |

---

## 15. Risks & Open Decisions

| # | Decision | Recommendation | Needs user input? |
|---|----------|----------------|-------------------|
| 1 | Grade level for initial test | Use student's registered `current_level` to pick Grade N question bank | Confirm grades 6–10 only |
| 2 | Speaking assessment format | Browser audio recording (requires mic permission) | Confirm acceptable |
| 3 | PDF library on Windows | WeasyPrint needs GTK; fallback to **xhtml2pdf** if install fails | Try WeasyPrint first |
| 4 | Keep teacher/admin roles? | Keep auth roles; strip peer features only | Confirm |
| 5 | Migrate old assessment JSON files? | Optional one-time import script | Low priority |
| 6 | English speaking content language | Assume English prompts; Nepal context in writing/science | Confirm |
| 7 | RTX 2050 VRAM | If <8 GB, use `phi3:mini` instead of Qwen 7B | Verify exact GPU spec |

---

## 16. Summary

This refactor transforms Edu Assist from an AI-heavy peer-tutoring prototype into a **reliable diagnostic assessment product**:

1. **Standardized four-area battery** — Speaking English, Writing English, Mathematics, Science.
2. **Elaborative topic reports** — strengths, weaknesses, and reasoning per topic.
3. **PDF learning guide + resource roadmap** — templated, downloadable, curated free links.
4. **Peer matching removed entirely** — backend, frontend, and DB.
5. **Efficient local AI** — Ollama + faster-whisper on RTX 2050; deterministic grading where possible.
6. **Same website theme** — restructured navigation and pages, preserved cream/charcoal palette.

**Estimated effort:** ~5–6 weeks for one full-stack developer, assuming speaking content bank is created in parallel.

**Start here:** Phase 0 (DB models + remove matching routes + Ollama setup).

---

*Related documents:*
- `pojectDocument.md` — original codebase analysis (partially outdated after this refactor)
- `README.md` — update after Phase 4
