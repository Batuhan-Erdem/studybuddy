from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from app.models import ChatRequest, ChatResponse, PDFAnalysisResponse, StudyPlanRequest, StudyPlanResponse, StructuredPlan
from app.crew_setup import run_study_crew
from app.graph_setup import run_study_graph
from app.chat_graph import run_chat_graph
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import json
import traceback
import asyncio

from app.pdf_utils import build_pdf_plan_goal, calculate_days_until, extract_text_from_pdf
from app.mcp_tools import read_pdf_via_mcp

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

@app.get("/")
def read_root():
    return {"message": "StudyBuddy backend is running"}

@app.post("/analyze-pdf", response_model=PDFAnalysisResponse)
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        # Proje dışı geçici klasör (Reload'ı engellemek için)
        upload_dir = Path("/tmp/studybuddy_uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
            
        # PDF meta bilgisini al (sayfa sayısı vb)
        _, page_count = extract_text_from_pdf(content)
        
        # MCP ile yapılandırılmış metni oku
        print(f"\n[MCP-CLIENT-İSTEĞİ] PDF analizi için uzman sunucuya bağlanılıyor: {file.filename}")
        pdf_text = await read_pdf_via_mcp(str(file_path))
        
        print(f"[MCP-CLIENT-YANITI] Uzman sunucudan veri başarıyla alındı. Karakter: {len(pdf_text)}")
        
        return PDFAnalysisResponse(
            status="success", 
            filename=file.filename, 
            page_count=page_count,
            content=pdf_text
        )
    except Exception as e:
        print(f"HATA (analyze-pdf): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plan-study-pdf", response_model=StudyPlanResponse)
async def plan_study_pdf(
    file: UploadFile = File(...),
    deadline: str = Form(...),
    hours_per_day: float = Form(...),
):
    try:
        days_left = calculate_days_until(deadline)
        if days_left < 1:
            days_left = 1 # Minimum 1 gün
            
        upload_dir = Path("/tmp/studybuddy_uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Dosya ismini güvenli hale getir veya benzersiz yap
        file_path = upload_dir / file.filename
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        print(f"DEBUG: MCP üzerinden PDF okunuyor: {file_path}")
        pdf_text = await read_pdf_via_mcp(str(file_path))
        
        if pdf_text.startswith("Error") or pdf_text.startswith("MCP Client Hatası"):
            raise HTTPException(status_code=500, detail=pdf_text)

        print(f"DEBUG: PDF başarıyla okundu. Karakter sayısı: {len(pdf_text)}")

        goal = build_pdf_plan_goal(pdf_text, deadline, hours_per_day)

        print("DEBUG: CrewAI PDF için çalışıyor...")
        result = run_study_crew(goal=goal, days=days_left, hours_per_day=hours_per_day)
        
        cleaned_result = str(result).strip()
        
        from json_repair import repair_json
        repaired = repair_json(cleaned_result, return_objects=False)
        parsed = json.loads(str(repaired).strip())
        structured_plan = StructuredPlan(**parsed)
        
        return StudyPlanResponse(status="success", plan=structured_plan, raw_text=cleaned_result)
    except Exception as e:
        print(f"HATA (plan-study-pdf): {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan-study", response_model=StudyPlanResponse)
def plan_study(request: StudyPlanRequest):
    try:
        result = run_study_crew(goal=request.goal, days=request.days, hours_per_day=request.hours_per_day)
        cleaned_result = str(result).strip()
        
        from json_repair import repair_json
        repaired = repair_json(cleaned_result, return_objects=False)
        parsed = json.loads(str(repaired).strip())
        structured_plan = StructuredPlan(**parsed)
        
        return StudyPlanResponse(status="success", plan=structured_plan, raw_text=cleaned_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = run_chat_graph(message=request.message, plan=request.plan, history=request.history)
    return ChatResponse(reply=reply)