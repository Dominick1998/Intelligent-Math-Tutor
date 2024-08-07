from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask_babel import Babel, _
import os
import logging
from logging.handlers import RotatingFileHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize the Flask application
app = Flask(__name__)

# Configure the database URI and other settings
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
app.config['BABEL_DEFAULT_LOCALE'] = 'en'

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
babel = Babel(app)

# Set up logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('Intelligent Math Tutor startup')

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Import models after initializing extensions to avoid circular imports
from backend.models import User, Progress, Problem, Feedback, Badge, Notification, Tutorial, LearningPath
from backend.utils import recommend_problem

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'es', 'fr', 'de'])

# Custom error handler for validation errors
@app.errorhandler(400)
def bad_request(error):
    app.logger.error(f'Bad Request: {error}')
    return jsonify({'message': _('Bad Request'), 'details': str(error)}), 400

# Custom error handler for unauthorized access
@app.errorhandler(401)
def unauthorized(error):
    app.logger.error(f'Unauthorized: {error}')
    return jsonify({'message': _('Unauthorized'), 'details': str(error)}), 401

# User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return bad_request(_('Missing username, email, or password'))

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return bad_request(_('User already exists'))

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error saving user data')}), 500

    return jsonify({'message': _('User registered successfully')}), 201

# User login endpoint
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return bad_request(_('Missing email or password'))

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity={'user_id': user.id, 'username': user.username, 'email': user.email})
        response = jsonify({'access_token': access_token})
        return response, 200

    return unauthorized(_('Invalid credentials'))

# User logout endpoint
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"message": _("Logout successful")})
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
    return jsonify({'message': _('User not found')}), 404

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
        return jsonify({'message': _('Profile updated successfully')}), 200
    return jsonify({'message': _('User not found')}), 404

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
    return jsonify({'message': _('User not found')}), 404

# Submit user feedback endpoint
@app.route('/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    current_user = get_jwt_identity()
    data = request.get_json()
    feedback_text = data.get('feedback')

    if not feedback_text:
        return bad_request(_('Missing feedback text'))

    feedback = Feedback(user_id=current_user['user_id'], feedback=feedback_text)
    db.session.add(feedback)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error saving feedback')}), 500

    return jsonify({'message': _('Feedback submitted successfully')}), 201

# Home route
@app.route('/')
def home():
    return _("Welcome to the Intelligent Math Tutor!")

# Track user progress endpoint
@app.route('/progress', methods=['POST'])
@jwt_required()
def track_progress():
    data = request.get_json()
    user_id = data.get('user_id')
    problem_id = data.get('problem_id')
    status = data.get('status')

    if not user_id or not problem_id or not status:
        return bad_request(_('Missing user_id, problem_id, or status'))

    new_progress = Progress(user_id=user_id, problem_id=problem_id, status=status)
    db.session.add(new_progress)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error saving progress data')}), 500

    return jsonify({'message': _('Progress tracked successfully')}), 201

# Get user progress endpoint
@app.route('/progress/<int:user_id>', methods=['GET'])
@jwt_required()
def get_progress(user_id):
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
        return jsonify({'message': _('No problems available')}), 404

# Get user analytics endpoint
@app.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['user_id']).first()
    if user:
        progress = Progress.query.filter_by(user_id=user.id).all()
        total_problems = len(progress)
        correct_answers = sum(1 for p in progress if p.status == 'completed')
        incorrect_answers = total_problems - correct_answers
        performance_ratio = correct_answers / total_problems if total_problems else 0
        feedback_count = Feedback.query.filter_by(user_id=user.id).count()
        return jsonify({
            'username': user.username,
            'email': user.email,
            'total_problems': total_problems,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'performance_ratio': performance_ratio,
            'feedback_count': feedback_count
        }), 200
    return jsonify({'message': _('User not found')}), 404

# Get user badges endpoint
@app.route('/badges', methods=['GET'])
@jwt_required()
def get_badges():
    current_user = get_jwt_identity()
    badges = Badge.query.filter_by(user_id=current_user['user_id']).all()
    badge_list = [{'name': b.name, 'description': b.description, 'date_awarded': b.date_awarded} for b in badges]
    return jsonify(badge_list), 200

# Award a badge to the user endpoint
@app.route('/award_badge', methods=['POST'])
@jwt_required()
def award_badge():
    data = request.get_json()
    badge_name = data.get('name')
    description = data.get('description')
    current_user = get_jwt_identity()

    if not badge_name or not description:
        return bad_request(_('Missing badge name or description'))

    badge = Badge(name=badge_name, description=description, user_id=current_user['user_id'])
    db.session.add(badge)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error awarding badge')}), 500

    return jsonify({'message': _('Badge awarded successfully')}), 201

# Get user notifications endpoint
@app.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=current_user['user_id']).all()
    notification_list = [{'message': n.message, 'date_sent': n.date_sent, 'is_read': n.is_read} for n in notifications]
    return jsonify(notification_list), 200

# Send a notification to the user endpoint
@app.route('/notifications', methods=['POST'])
@jwt_required()
def send_notification():
    data = request.get_json()
    message = data.get('message')
    current_user = get_jwt_identity()

    if not message:
        return bad_request(_('Missing notification message'))

    notification = Notification(message=message, user_id=current_user['user_id'])
    db.session.add(notification)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error sending notification')}), 500

    return jsonify({'message': _('Notification sent successfully')}), 201

# Mark a notification as read endpoint
@app.route('/notifications/read/<int:id>', methods=['POST'])
@jwt_required()
def mark_as_read(id):
    current_user = get_jwt_identity()
    notification = Notification.query.filter_by(id=id, user_id=current_user['user_id']).first()
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'message': _('Notification marked as read')}), 200
    return jsonify({'message': _('Notification not found')}), 404

# Get all tutorials
@app.route('/tutorials', methods=['GET'])
def get_tutorials():
    tutorials = Tutorial.query.all()
    tutorial_list = [{'id': t.id, 'title': t.title, 'content': t.content, 'problem_id': t.problem_id, 'date_created': t.date_created} for t in tutorials]
    return jsonify(tutorial_list), 200

# Add a new tutorial
@app.route('/tutorials', methods=['POST'])
@jwt_required()
def add_tutorial():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    problem_id = data.get('problem_id')
    current_user = get_jwt_identity()

    if not title or not content or not problem_id:
        return bad_request(_('Missing title, content, or problem_id'))

    tutorial = Tutorial(title=title, content=content, problem_id=problem_id)
    db.session.add(tutorial)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error saving tutorial')}), 500

    return jsonify({'message': _('Tutorial added successfully')}), 201

# Get a specific tutorial
@app.route('/tutorials/<int:id>', methods=['GET'])
def get_tutorial(id):
    tutorial = Tutorial.query.filter_by(id=id).first()
    if tutorial:
        return jsonify({'id': tutorial.id, 'title': tutorial.title, 'content': tutorial.content, 'problem_id': tutorial.problem_id, 'date_created': tutorial.date_created}), 200
    return jsonify({'message': _('Tutorial not found')}), 404

# Get learning path for a user
@app.route('/learning_path/<int:user_id>', methods=['GET'])
@jwt_required()
def get_learning_path(user_id):
    learning_path = LearningPath.query.filter_by(user_id=user_id).first()
    if learning_path:
        return jsonify({'user_id': learning_path.user_id, 'problems': learning_path.problems, 'date_created': learning_path.date_created}), 200
    return jsonify({'message': _('Learning path not found')}), 404

# Create or update learning path for a user
@app.route('/learning_path', methods=['POST'])
@jwt_required()
def create_update_learning_path():
    data = request.get_json()
    user_id = data.get('user_id')
    problems = data.get('problems')

    if not user_id or not problems:
        return bad_request(_('Missing user_id or problems'))

    learning_path = LearningPath.query.filter_by(user_id=user_id).first()
    if learning_path:
        learning_path.problems = problems
    else:
        learning_path = LearningPath(user_id=user_id, problems=problems)
        db.session.add(learning_path)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error saving learning path')}), 500

    return jsonify({'message': _('Learning path saved successfully')}), 201

# Get all users
@app.route('/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    user_list = [{'id': u.id, 'username': u.username, 'email': u.email} for u in users]
    return jsonify(user_list), 200

# Delete a user
@app.route('/admin/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': _('User deleted successfully')}), 200
    return jsonify({'message': _('User not found')}), 404

# Get all feedback
@app.route('/admin/feedback', methods=['GET'])
@jwt_required()
def get_feedback():
    feedback = Feedback.query.all()
    feedback_list = [{'id': f.id, 'user_id': f.user_id, 'feedback': f.feedback, 'timestamp': f.timestamp} for f in feedback]
    return jsonify(feedback_list), 200

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
