from backend.models import Problem, Progress
import random

def recommend_problem(user_id):
    # Retrieve user progress
    progress = Progress.query.filter_by(user_id=user_id).all()
    completed_problems = {p.problem_id for p in progress}

    # Retrieve user's performance metrics
    correct_answers = sum(1 for p in progress if p.status == 'completed')
    incorrect_answers = len(progress) - correct_answers
    performance_ratio = correct_answers / len(progress) if progress else 1

    # Filter out completed problems and categorize by difficulty
    easy_problems = Problem.query.filter(~Problem.id.in_(completed_problems), Problem.difficulty == 'easy').all()
    medium_problems = Problem.query.filter(~Problem.id.in_(completed_problems), Problem.difficulty == 'medium').all()
    hard_problems = Problem.query.filter(~Problem.id.in_(completed_problems), Problem.difficulty == 'hard').all()

    # Recommendation logic based on performance ratio
    if performance_ratio >= 0.75:
        recommended_problem = random.choice(hard_problems) if hard_problems else None
    elif performance_ratio >= 0.5:
        recommended_problem = random.choice(medium_problems) if medium_problems else None
    else:
        recommended_problem = random.choice(easy_problems) if easy_problems else None

    return recommended_problem
