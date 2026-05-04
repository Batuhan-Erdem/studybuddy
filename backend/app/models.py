from pydantic import BaseModel
from typing import List, Literal

class DayPlan(BaseModel):
    day: int
    focus: str
    duration_hours: float
    tasks: List[str]

class StructuredPlan(BaseModel):
    title: str
    days: List[DayPlan]
    tips: List[str]

class StudyPlanRequest(BaseModel):
    goal: str
    days: int
    hours_per_day: float

class StudyPlanResponse(BaseModel):
    status: str
    plan: StructuredPlan
    raw_text: str | None = None


class PDFAnalysisResponse(BaseModel):
    status: str
    filename: str
    page_count: int


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    plan: StructuredPlan | None = None
    history: List[ChatMessage] | None = None


class ChatResponse(BaseModel):
    reply: str