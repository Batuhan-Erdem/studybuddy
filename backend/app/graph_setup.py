from __future__ import annotations

import json
import os
from typing import Any, Literal, NotRequired, TypedDict

from app.models import StructuredPlan


class StudyGraphState(TypedDict):
    goal: str
    days: int
    hours_per_day: float
    user_input: str
    draft_json: str
    attempt: int
    errors: list[str]
    structured_plan: NotRequired[StructuredPlan]


def _get_llm():
    from langchain_openai import ChatOpenAI

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0.2)


def _detect_language(text: str) -> Literal["tr", "en"]:
    turkish_chars = set("çğıöşüÇĞİÖŞÜ")
    if any(ch in turkish_chars for ch in text):
        return "tr"
    return "tr" if any(word in text.lower() for word in ("ve", "için", "gün", "saat")) else "en"


def _build_user_input(state: StudyGraphState) -> dict[str, Any]:
    user_input = (
        f"The student goal is: {state['goal']}. "
        f"They have {state['days']} days and can study {state['hours_per_day']} hours per day."
    )
    return {"user_input": user_input}


def _plan_node(state: StudyGraphState) -> dict[str, Any]:
    from langchain_core.messages import HumanMessage, SystemMessage

    lang = _detect_language(state["goal"])
    system = (
        "You are an expert academic planner. "
        "Return ONLY valid JSON. Do not add markdown. Do not add explanations. "
        "JSON must match this shape exactly: "
        "{\"title\": string, \"days\": [{\"day\": number, \"focus\": string, \"duration_hours\": number, \"tasks\": [string]}], \"tips\": [string]} "
        "Language rule: respond ONLY in the same language as the user's goal."
    )
    user = (
        f"USER_GOAL_LANGUAGE={lang}\n"
        f"Create a structured day-by-day study plan for this user input:\n"
        f"{state['user_input']}"
    )

    llm = _get_llm()
    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return {"draft_json": str(response.content).strip()}


def _breakdown_node(state: StudyGraphState) -> dict[str, Any]:
    from langchain_core.messages import HumanMessage, SystemMessage

    lang = _detect_language(state["goal"])
    system = (
        "You are a task breakdown specialist. "
        "Improve the plan to be more practical and actionable, while keeping the same JSON shape. "
        "Return ONLY valid JSON. Do not add markdown. Do not add explanations. "
        "Language rule: keep the same language as the input plan."
    )
    user = (
        f"USER_GOAL_LANGUAGE={lang}\n"
        "Here is the draft plan JSON to improve (return corrected/improved JSON only):\n"
        f"{state['draft_json']}"
    )

    llm = _get_llm()
    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return {"draft_json": str(response.content).strip()}


def _validate_node(state: StudyGraphState) -> dict[str, Any]:
    try:
        parsed = json.loads(state["draft_json"])
        structured_plan = StructuredPlan(**parsed)
        return {"structured_plan": structured_plan}
    except Exception as exc:
        errors = list(state.get("errors", []))
        errors.append(str(exc))
        return {"errors": errors}


def _repair_node(state: StudyGraphState) -> dict[str, Any]:
    from json_repair import repair_json

    attempt = int(state.get("attempt", 0)) + 1
    repaired = repair_json(state["draft_json"], return_objects=False)
    return {"draft_json": str(repaired).strip(), "attempt": attempt}


def _fallback_node(state: StudyGraphState) -> dict[str, Any]:
    fallback_plan = StructuredPlan(title="Generated Study Plan", days=[], tips=[])
    return {"structured_plan": fallback_plan}


def build_study_graph(max_attempts: int = 3):
    from langgraph.graph import END, StateGraph

    graph = StateGraph(StudyGraphState)
    graph.add_node("build_input", _build_user_input)
    graph.add_node("plan", _plan_node)
    graph.add_node("breakdown", _breakdown_node)
    graph.add_node("validate", _validate_node)
    graph.add_node("repair", _repair_node)
    graph.add_node("fallback", _fallback_node)

    graph.set_entry_point("build_input")
    graph.add_edge("build_input", "plan")
    graph.add_edge("plan", "breakdown")
    graph.add_edge("breakdown", "validate")

    def route_after_validate(state: StudyGraphState):
        if state.get("structured_plan") is not None:
            return END
        if int(state.get("attempt", 0)) >= max_attempts:
            return "fallback"
        return "repair"

    graph.add_conditional_edges(
        "validate",
        route_after_validate,
        {
            END: END,
            "repair": "repair",
            "fallback": "fallback",
        },
    )
    graph.add_edge("repair", "validate")
    graph.add_edge("fallback", END)

    return graph.compile()


def run_study_graph(goal: str, days: int, hours_per_day: float) -> StructuredPlan:
    app = build_study_graph(max_attempts=3)
    state: StudyGraphState = {
        "goal": goal,
        "days": days,
        "hours_per_day": hours_per_day,
        "user_input": "",
        "draft_json": "",
        "attempt": 0,
        "errors": [],
    }
    final_state = app.invoke(state)
    structured_plan = final_state.get("structured_plan")
    if structured_plan is None:
        raise RuntimeError("LangGraph did not produce a structured plan")
    return structured_plan
