from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask_babel import Babel, _
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import os
import logging
from logging.handlers import RotatingFileHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random
from backend.chatbot import Chatbot
from backend.progress_report import send_progress_report

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
socketio = SocketIO(app, cors_allowed_origins="*")
chatbot = Chatbot()  # Initialize chatbot

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
from backend.models import User, Progress, Problem, Feedback, Badge, Notification, Tutorial, LearningPath, Hint, Comment, ForumPost
from backend.utils import recommend_problem

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'es', 'fr', 'de', 'it'])

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
            'total_problems': total_problems,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'performance_ratio': performance_ratio,
            'feedback_count': feedback_count
        }), 200
    return jsonify({'message': _('User not found')}), 404

# Create a learning path for a user
@app.route('/learning-path', methods=['POST'])
@jwt_required()
def create_learning_path():
    data = request.get_json()
    path_description = data.get('path_description')

    if not path_description:
        return bad_request(_('Missing path description'))

    new_path = LearningPath(user_id=get_jwt_identity()['user_id'], path_description=path_description)
    db.session.add(new_path)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error creating learning path')}), 500

    return jsonify({'message': _('Learning path created successfully')}), 201

# Get learning paths for a user
@app.route('/learning-path/<int:user_id>', methods=['GET'])
@jwt_required()
def get_learning_paths(user_id):
    paths = LearningPath.query.filter_by(user_id=user_id).all()
    path_list = [{'id': p.id, 'path_description': p.path_description, 'timestamp': p.timestamp} for p in paths]
    return jsonify(path_list), 200

# Add a hint to a problem
@app.route('/hint', methods=['POST'])
@jwt_required()
def add_hint():
    data = request.get_json()
    problem_id = data.get('problem_id')
    hint_text = data.get('hint_text')

    if not problem_id or not hint_text:
        return bad_request(_('Missing problem_id or hint_text'))

    new_hint = Hint(problem_id=problem_id, hint_text=hint_text)
    db.session.add(new_hint)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error adding hint')}), 500

    return jsonify({'message': _('Hint added successfully')}), 201

# Get hints for a problem
@app.route('/hint/<int:problem_id>', methods=['GET'])
@jwt_required()
def get_hints(problem_id):
    hints = Hint.query.filter_by(problem_id=problem_id).all()
    hint_list = [{'id': h.id, 'hint_text': h.hint_text, 'timestamp': h.timestamp} for h in hints]
    return jsonify(hint_list), 200

# Add a comment to a discussion
@app.route('/comment', methods=['POST'])
@jwt_required()
def add_comment():
    data = request.get_json()
    discussion_id = data.get('discussion_id')
    comment_text = data.get('comment_text')

    if not discussion_id or not comment_text:
        return bad_request(_('Missing discussion_id or comment_text'))

    new_comment = Comment(discussion_id=discussion_id, user_id=get_jwt_identity()['user_id'], comment_text=comment_text)
    db.session.add(new_comment)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error adding comment')}), 500

    return jsonify({'message': _('Comment added successfully')}), 201

# Get comments for a discussion
@app.route('/comment/<int:discussion_id>', methods=['GET'])
@jwt_required()
def get_comments(discussion_id):
    comments = Comment.query.filter_by(discussion_id=discussion_id).all()
    comment_list = [{'id': c.id, 'user_id': c.user_id, 'comment_text': c.comment_text, 'timestamp': c.timestamp} for c in comments]
    return jsonify(comment_list), 200

# Real-Time Collaboration - Socket.IO event handlers
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    send({'message': f'{data["username"]} has entered the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    send({'message': f'{data["username"]} has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    emit('response', {'message': data['message']}, room=data['room'])

# Shared Whiteboard for real-time collaboration
@socketio.on('draw')
def handle_draw(data):
    room = data['room']
    emit('draw', data['drawData'], to=room)

# Chatbot for assistance
@app.route('/chatbot', methods=['POST'])
@jwt_required()
def chatbot_response():
    data = request.get_json()
    user_input = data.get('message')
    if not user_input:
        return bad_request(_('Missing message'))
    
    response = chatbot.get_response(user_input)
    return jsonify({'message': response}), 200

# Progress report generation
@app.route('/send_report', methods=['POST'])
@jwt_required()
def send_report():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['user_id']).first()
    if user:
        send_progress_report(user)
        return jsonify({'message': _('Progress report sent')}), 200
    return jsonify({'message': _('User not found')}), 404

# Run the application
if __name__ == '__main__':
    socketio.run(app, debug=True)
