from crewai import Agent

def get_planner_agent():
    return Agent(
        role="Academic Planner",
        goal="Create an efficient study plan based on user's goals and time constraints",
        backstory="You are an expert academic planner helping students optimize their study time.",
        verbose=True
    )

def get_breakdown_agent():
    return Agent(
        role="Task Breakdown Specialist",
        goal="Break down study plans into small actionable tasks",
        backstory="You specialize in turning big goals into simple step-by-step tasks.",
        verbose=True
    )