from __future__ import annotations

import os
from typing import Any, Literal, NotRequired, TypedDict

from app.models import ChatMessage, StructuredPlan


class ChatGraphState(TypedDict):
    message: str
    plan: StructuredPlan | None
    history: list[ChatMessage]
    reply: NotRequired[str]


def _get_llm():
    from langchain_openai import ChatOpenAI

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0.2)


def _detect_language(text: str) -> Literal["tr", "en"]:
    turkish_chars = set("çğıöşüÇĞİÖŞÜ")
    if any(ch in turkish_chars for ch in text):
        return "tr"
    return "tr" if any(word in text.lower() for word in ("ve", "için", "gün", "saat")) else "en"


def _history_to_text(history: list[ChatMessage], max_items: int = 10) -> str:
    trimmed = history[-max_items:]
    lines: list[str] = []
    for item in trimmed:
        role = "User" if item.role == "user" else "Assistant"
        lines.append(f"{role}: {item.content}")
    return "\n".join(lines)


def _answer_no_plan(state: ChatGraphState) -> dict[str, Any]:
    lang = _detect_language(state["message"])
    if lang == "tr":
        reply = (
            "Henüz bir çalışma planı görmüyorum. Önce ‘Plan Oluştur’ ile planı üret, "
            "sonra planla ilgili sorularını buradan sorabilirsin."
        )
    else:
        reply = (
            "I can’t see a study plan yet. Please generate a plan first using ‘Create Plan’, "
            "then ask your questions here."
        )
    return {"reply": reply}


def _answer_with_plan(state: ChatGraphState) -> dict[str, Any]:
    from langchain_core.messages import HumanMessage, SystemMessage

    lang = _detect_language(state["message"])
    plan = state["plan"]
    plan_payload = plan.model_dump() if plan is not None else None

    system_tr = (
        "Sen StudyBuddy Plan Asistanısın. Kullanıcının verdiği çalışma planına dayanarak soruları yanıtla. "
        "Kısa ve net ol. Gerektiğinde gün numarası ver ve somut öneri üret. "
        "Eğer kullanıcı planı değiştirmek isterse, değiştirilmiş bir plan JSON’u üretme; yalnızca metin olarak öneri sun."
    )
    system_en = (
        "You are the StudyBuddy Plan Assistant. Answer questions using the provided study plan. "
        "Be concise and actionable. Mention day numbers when helpful. "
        "If the user asks to modify the plan, do not output plan JSON; provide suggestions in plain text."
    )

    system = system_tr if lang == "tr" else system_en
    history_text = _history_to_text(state.get("history", []), max_items=10)

    user = (
        "STUDY_PLAN_JSON:\n"
        f"{plan_payload}\n\n"
        "CONVERSATION_HISTORY:\n"
        f"{history_text}\n\n"
        "USER_MESSAGE:\n"
        f"{state['message']}\n"
    )

    llm = _get_llm()
    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return {"reply": str(response.content).strip()}


def build_chat_graph():
    from langgraph.graph import END, StateGraph

    graph = StateGraph(ChatGraphState)
    graph.add_node("route", lambda state: {})
    graph.add_node("no_plan", _answer_no_plan)
    graph.add_node("with_plan", _answer_with_plan)

    def route(state: ChatGraphState):
        return "no_plan" if state.get("plan") is None else "with_plan"

    graph.set_entry_point("route")
    graph.add_conditional_edges("route", route, {"no_plan": "no_plan", "with_plan": "with_plan"})
    graph.add_edge("no_plan", END)
    graph.add_edge("with_plan", END)

    return graph.compile()


def run_chat_graph(
    message: str,
    plan: StructuredPlan | None,
    history: list[ChatMessage] | None,
) -> str:
    app = build_chat_graph()
    state: ChatGraphState = {
        "message": message,
        "plan": plan,
        "history": history or [],
    }
    final_state = app.invoke(state)
    reply = final_state.get("reply")
    if not reply:
        raise RuntimeError("Chat graph did not produce a reply")
    return str(reply)
