from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from flask_migrate import Migrate

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
    db.session.commit()

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
        return jsonify({'access_token': access_token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

# Home route
@app.route('/')
def home():
    return "Welcome to the Intelligent Math Tutor!"

# Track user progress endpoint
@app.route('/progress', methods=['POST'])
def track_progress():
    data = request.get_json()
    user_id = data.get('user_id')
    problem_id = data.get('problem_id')
    status = data.get('status')

    # Create a new progress entry
    new_progress = Progress(user_id=user_id, problem_id=problem_id, status=status)
    db.session.add(new_progress)
    db.session.commit()

    return jsonify({'message': 'Progress tracked successfully'}), 201

# Get user progress endpoint
@app.route('/progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    # Retrieve all progress entries for the given user
    progress = Progress.query.filter_by(user_id=user_id).all()
    progress_list = [{'problem_id': p.problem_id, 'status': p.status, 'timestamp': p.timestamp} for p in progress]
    return jsonify(progress_list), 200

# Recommend a problem for the user
@app.route('/recommend/<int:user_id>', methods=['GET'])
def recommend(user_id):
    recommended_problem = recommend_problem(user_id)
    if recommended_problem:
        return jsonify({
            'problem_id': recommended_problem.id,
            'question': recommended_problem.question,
            'difficulty': recommended_problem.difficulty
        }), 200
    else:
        return jsonify({'message': 'No problems available'}), 404

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
