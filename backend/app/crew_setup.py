from crewai import Crew, Process
from app.agents import get_planner_agent, get_breakdown_agent
from app.tasks import create_planning_task, create_breakdown_task

def run_study_crew(goal: str, days: int, hours_per_day: float):
    planner = get_planner_agent()
    breakdown = get_breakdown_agent()

    user_input = (
        f"The student goal is: {goal}. "
        f"They have {days} days and can study {hours_per_day} hours per day."
    )

    planning_task = create_planning_task(planner, user_input)
    breakdown_task = create_breakdown_task(breakdown, planning_task)

    crew = Crew(
        agents=[planner, breakdown],
        tasks=[planning_task, breakdown_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    return str(result)