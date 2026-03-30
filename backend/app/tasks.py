from crewai import Task

def create_planning_task(agent, user_input):
    return Task(
        description=f"""
        The user said: "{user_input}"

        Create a structured study plan.

        You must organize the plan by days.
        For each day include:
        - day number
        - focus topic
        - duration in hours
        - short actionable tasks

        Also include a short list of study tips.

        LANGUAGE RULE (VERY IMPORTANT):
        - Detect the language of the user's input.
        - Respond ONLY in that language.
        - If the user writes in Turkish, respond in Turkish.
        - If the user writes in English, respond in English.
        - NEVER mix languages.

        IMPORTANT:
        Return the result in a clean JSON-style structure using these keys exactly:
        title, days, day, focus, duration_hours, tasks, tips
        """,
        agent=agent,
        expected_output="A structured day-by-day study plan in JSON-style format, in the same language as the user."
    )


def create_breakdown_task(agent, planning_task):
    return Task(
        description="""
        Take the planner agent's study plan and improve it into a more practical structured plan.

        LANGUAGE RULE (VERY IMPORTANT):
        - Keep the SAME language as the input plan.
        - Do NOT translate.
        - Do NOT mix languages.

        IMPORTANT:
        Return the final answer in valid JSON only.
        Use exactly this shape:

        {
          "title": "string",
          "days": [
            {
              "day": 1,
              "focus": "string",
              "duration_hours": 2,
              "tasks": ["task 1", "task 2", "task 3"]
            }
          ],
          "tips": ["tip 1", "tip 2"]
        }

        Do not add markdown.
        Do not add explanations before or after JSON.
        Return JSON only.
        """,
        agent=agent,
        context=[planning_task],
        expected_output="Valid JSON with title, days, and tips in the same language as input."
    )