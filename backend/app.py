from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

# Initialize the Flask application
app = Flask(__name__)

# Configure the database URI and other settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite for simplicity; update as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications to save resources
app.config['SECRET_KEY'] = 'your_secret_key'  # Secret key for session management
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Secret key for JWT

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Import models after initializing extensions to avoid circular imports
from backend.models import User, Progress, Problem
from backend.utils import recommend_problem

# User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if the user already exists
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    # Hash the password and create a new user
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error saving user data'}), 500

    return jsonify({'message': 'User registered successfully'}), 201

# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Find the user by email
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        # Create a JWT access token
        access_token = create_access_token(identity={'user_id': user.id, 'username': user.username, 'email': user.email})
        response = jsonify({'access_token': access_token})
        return response, 200

    return jsonify({'message': 'Invalid credentials'}), 401

# User logout endpoint
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200

# Get user profile endpoint
@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['user_id']).first()
    if user:
        return jsonify({
            'username': user.username,
            'email': user.email
        }), 200
    return jsonify({'message': 'User not found'}), 404

# Update user profile endpoint
@app.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    data = request.get_json()
    user = User.query.filter_by(id=current_user['user_id']).first()
    if user:
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

# Get user dashboard data endpoint
@app.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['user_id']).first()
    if user:
        progress = Progress.query.filter_by(user_id=user.id).all()
        total_problems = len(progress)
        correct_answers = sum(1 for p in progress if p.status == 'completed')
        incorrect_answers = total_problems - correct_answers
        performance_ratio = correct_answers / total_problems if total_problems else 0
        return jsonify({
            'username': user.username,
            'email': user.email,
            'total_problems': total_problems,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'performance_ratio': performance_ratio
        }), 200
    return jsonify({'message': 'User not found'}), 404

# Home route
@app.route('/')
def home():
    return "Welcome to the Intelligent Math Tutor!"

# Track user progress endpoint
@app.route('/progress', methods=['POST'])
@jwt_required()
def track_progress():
    data = request.get_json()
    user_id = data.get('user_id')
    problem_id = data.get('problem_id')
    status = data.get('status')

    # Validate input data
    if not user_id or not problem_id or not status:
        return jsonify({'message': 'Invalid input data'}), 400

    # Create a new progress entry
    new_progress = Progress(user_id=user_id, problem_id=problem_id, status=status)
    db.session.add(new_progress)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error saving progress data'}), 500

    return jsonify({'message': 'Progress tracked successfully'}), 201

# Get user progress endpoint
@app.route('/progress/<int:user_id>', methods=['GET'])
@jwt_required()
def get_progress(user_id):
    # Retrieve all progress entries for the given user
    progress = Progress.query.filter_by(user_id=user_id).all()
    progress_list = [{'problem_id': p.problem_id, 'status': p.status, 'timestamp': p.timestamp} for p in progress]
    return jsonify(progress_list), 200

# Recommend a problem for the user
@app.route('/recommend/<int:user_id>', methods=['GET'])
@jwt_required()
def recommend(user_id):
    recommended_problem = recommend_problem(user_id)
    if recommended_problem:
        return jsonify({
            'problem_id': recommended_problem.id,
            'question': recommended_problem.question,
            'difficulty': recommended_problem.difficulty,
            'feedback': recommended_problem.feedback
        }), 200
    else:
        return jsonify({'message': 'No problems available'}), 404

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
