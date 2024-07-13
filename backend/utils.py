from backend.models import Problem, Progress
import random

def recommend_problem(user_id):
    # Retrieve user progress
    progress = Progress.query.filter_by(user_id=user_id).all()
    completed_problems = {p.problem_id for p in progress}

    # Filter out completed problems and categorize by difficulty
    easy_problems = Problem.query.filter(~Problem.id.in_(completed_problems), Problem.difficulty == 'easy').all()
    medium_problems = Problem.query.filter(~Problem.id.in_(completed_problems), Problem.difficulty == 'medium').all()
    hard_problems = Problem.query.filter(~Problem.id.in_(completed_problems), Problem.difficulty == 'hard').all()

    # Example logic to recommend a problem based on user's performance
    if len(completed_problems) < 5:
        recommended_problem = random.choice(easy_problems) if easy_problems else None
    elif len(completed_problems) < 10:
        recommended_problem = random.choice(medium_problems) if medium_problems else None
    else:
        recommended_problem = random.choice(hard_problems) if hard_problems else None

    return recommended_problem
