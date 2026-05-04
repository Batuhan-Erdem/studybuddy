from __future__ import annotations

from datetime import date, datetime
from io import BytesIO

import pdfplumber


def extract_text_from_pdf(pdf_bytes: bytes) -> tuple[str, int]:
    """PDF içeriğini düz metin olarak çıkarır."""
    text_parts: list[str] = []

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text.strip())

    return "\n".join(text_parts).strip(), page_count


def calculate_days_until(deadline_iso: str) -> int:
    """ISO tarihinden bugüne kalan gün sayısını döndürür."""
    deadline_date = date.fromisoformat(deadline_iso)
    today = date.today()
    return (deadline_date - today).days


def build_pdf_plan_goal(pdf_text: str, deadline_iso: str, hours_per_day: float) -> str:
    """PDF planlama için LLM'e gönderilecek kısa yönlendirme metni oluşturur."""
    preview = " ".join(pdf_text.split())[:1200]
    return (
        "Create a structured study plan based on this PDF assignment. "
        f"Deadline: {deadline_iso}. "
        f"Daily study hours: {hours_per_day}. "
        "Use the PDF context below and make the plan practical. "
        f"PDF content: {preview}"
    )