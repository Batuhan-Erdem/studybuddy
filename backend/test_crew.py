from app.crew_setup import run_study_crew

if __name__ == "__main__":
    user_input = "I have an AI exam in 3 days. I can study 2 hours per day."

    result = run_study_crew(user_input)
    print("\nFINAL RESULT:\n")
    print(result)