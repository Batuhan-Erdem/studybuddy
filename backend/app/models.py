from pydantic import BaseModel
from typing import List

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