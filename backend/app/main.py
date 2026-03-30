from fastapi import FastAPI, HTTPException
from app.models import StudyPlanRequest, StudyPlanResponse, StructuredPlan
from app.crew_setup import run_study_crew
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "StudyBuddy backend is running"}

@app.post("/plan-study", response_model=StudyPlanResponse)
def plan_study(request: StudyPlanRequest):
    try:
        result = run_study_crew(
            goal=request.goal,
            days=request.days,
            hours_per_day=request.hours_per_day
        )

        cleaned_result = str(result).strip()

        try:
            parsed = json.loads(cleaned_result)
            structured_plan = StructuredPlan(**parsed)

            return StudyPlanResponse(
                status="success",
                plan=structured_plan,
                raw_text=None
            )

        except Exception:
            fallback_plan = StructuredPlan(
                title="Generated Study Plan",
                days=[],
                tips=[]
            )

            return StudyPlanResponse(
                status="success",
                plan=fallback_plan,
                raw_text=cleaned_result
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))