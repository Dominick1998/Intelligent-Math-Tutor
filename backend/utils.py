from backend.models import Problem, Progress
import random

def recommend_problem(user_id):
    # Retrieve user progress
    progress = Progress.query.filter_by(user_id=user_id).all()
    completed_problems = {p.problem_id for p in progress}

    # Filter out completed problems and sort by difficulty
    remaining_problems = Problem.query.filter(~Problem.id.in_(completed_problems)).order_by(Problem.difficulty).all()

    # If there are no remaining problems, return None
    if not remaining_problems:
        return None

    # Simple recommendation logic (e.g., random selection from remaining problems)
    recommended_problem = random.choice(remaining_problems)

    return recommended_problem
