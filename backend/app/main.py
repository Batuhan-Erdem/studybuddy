from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from app.models import ChatRequest, ChatResponse, PDFAnalysisResponse, StudyPlanRequest, StudyPlanResponse, StructuredPlan
from app.crew_setup import run_study_crew
from app.graph_setup import run_study_graph
from app.chat_graph import run_chat_graph
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import json

from app.pdf_utils import build_pdf_plan_goal, calculate_days_until, extract_text_from_pdf

_backend_dir = Path(__file__).resolve().parents[1]
_repo_dir = _backend_dir.parent
load_dotenv(_repo_dir / ".env")
load_dotenv(_backend_dir / ".env")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/")
def read_root():
    return {"message": "StudyBuddy backend is running"}


@app.post("/analyze-pdf", response_model=PDFAnalysisResponse)
async def analyze_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Lütfen bir PDF dosyası yükleyin")

    pdf_bytes = await file.read()
    _, page_count = extract_text_from_pdf(pdf_bytes)

    return PDFAnalysisResponse(
        status="success",
        filename=file.filename,
        page_count=page_count,
    )


@app.post("/plan-study-pdf", response_model=StudyPlanResponse)
async def plan_study_pdf(
    file: UploadFile = File(...),
    deadline: str = Form(...),
    hours_per_day: float = Form(...),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Lütfen bir PDF dosyası yükleyin")

    days_left = calculate_days_until(deadline)
    if days_left <= 0:
        raise HTTPException(status_code=400, detail="Deadline bugünden sonra bir tarih olmalı")

    pdf_bytes = await file.read()
    pdf_text, _ = extract_text_from_pdf(pdf_bytes)
    goal = build_pdf_plan_goal(pdf_text, deadline, hours_per_day)

    try:
        structured_plan = run_study_graph(
            goal=goal,
            days=days_left,
            hours_per_day=hours_per_day,
        )
        return StudyPlanResponse(status="success", plan=structured_plan, raw_text=None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
            try:
                from json_repair import repair_json

                repaired = repair_json(cleaned_result, return_objects=False)
                parsed = json.loads(str(repaired).strip())
                structured_plan = StructuredPlan(**parsed)
                return StudyPlanResponse(
                    status="success",
                    plan=structured_plan,
                    raw_text=cleaned_result,
                )
            except Exception:
                structured_plan = run_study_graph(
                    goal=request.goal,
                    days=request.days,
                    hours_per_day=request.hours_per_day,
                )
                return StudyPlanResponse(
                    status="success",
                    plan=structured_plan,
                    raw_text=cleaned_result,
                )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan-study-graph", response_model=StudyPlanResponse)
def plan_study_graph(request: StudyPlanRequest):
    try:
        structured_plan = run_study_graph(
            goal=request.goal,
            days=request.days,
            hours_per_day=request.hours_per_day,
        )

        return StudyPlanResponse(status="success", plan=structured_plan, raw_text=None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        reply = run_chat_graph(
            message=request.message,
            plan=request.plan,
            history=request.history,
        )
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))