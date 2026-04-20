# LangSmith tracing (StudyBuddy)

## Setup
- Ensure `backend/.env` is NOT committed (already ignored by `.gitignore`).
- Set these variables in `backend/.env`:
  - `LANGSMITH_TRACING=true`
  - `LANGSMITH_PROJECT=studybuddy`
  - `LANGSMITH_API_KEY=...`

(Optional)
- If you need a specific model for the LangGraph path:
  - `OPENAI_MODEL=gpt-4o-mini`

## Run
From the `backend/` folder:
- Start API: `./.venv/bin/uvicorn app.main:app --reload`
- Call LangGraph endpoint: `POST http://127.0.0.1:8000/plan-study-graph`

## Verify
- Open your LangSmith dashboard.
- Select the `studybuddy` project.
- You should see a trace with nodes corresponding to the graph steps (plan/breakdown/validate/repair/fallback).

## Notes
- Tracing only appears if `LANGSMITH_API_KEY` is set.
- Never paste keys into README or commit them to git.
