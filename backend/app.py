from flask import Flask, request, jsonify, make_response
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
from flask import Flask
from backend.routes import api_bp
from backend.logging_middleware import log_request_and_response
from backend.log_rotation import setup_log_rotation

# Set up log rotation
setup_log_rotation()

# Initialize the Flask application
app = Flask(__name__)

# Apply logging middleware to log requests and responses
app = log_request_and_response(app)

# Register the Blueprint for API routes
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)

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
from backend.models import User, Progress, Problem, Feedback, Badge, Notification, Tutorial, LearningPath, Hint, Comment, Vote, Report, Follow, Message, Discussion, DiscussionTopic, DiscussionPost
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

# Follow a user
@app.route('/follow/<int:followed_id>', methods=['POST'])
@jwt_required()
def follow_user(followed_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['user_id']).first()
    if user:
        followed_user = User.query.get(followed_id)
        if followed_user:
            follow = Follow(follower_id=user.id, followed_id=followed_id)
            db.session.add(follow)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return jsonify({'message': _('Error following user')}), 500
            return jsonify({'message': _('User followed successfully')}), 201
        else:
            return bad_request(_('User not found'))
    return unauthorized(_('Unauthorized'))

# Unfollow a user
@app.route('/unfollow/<int:followed_id>', methods=['DELETE'])
@jwt_required()
def unfollow_user(followed_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user['user_id']).first()
    if user:
        follow = Follow.query.filter_by(follower_id=user.id, followed_id=followed_id).first()
        if follow:
            db.session.delete(follow)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return jsonify({'message': _('Error unfollowing user')}), 500
            return jsonify({'message': _('User unfollowed successfully')}), 200
        else:
            return bad_request(_('Not following this user'))
    return unauthorized(_('Unauthorized'))

# Send a private message
@app.route('/message', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    message_text = data.get('message_text')

    if not recipient_id or not message_text:
        return bad_request(_('Missing recipient_id or message_text'))

    current_user = get_jwt_identity()
    new_message = Message(sender_id=current_user['user_id'], recipient_id=recipient_id, message_text=message_text)
    db.session.add(new_message)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error sending message')}), 500

    return jsonify({'message': _('Message sent successfully')}), 201

# Get messages for a user
@app.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    current_user = get_jwt_identity()
    received_messages = Message.query.filter_by(recipient_id=current_user['user_id']).all()
    sent_messages = Message.query.filter_by(sender_id=current_user['user_id']).all()

    messages = {
        'received': [{'id': m.id, 'sender_id': m.sender_id, 'message_text': m.message_text, 'timestamp': m.timestamp} for m in received_messages],
        'sent': [{'id': m.id, 'recipient_id': m.recipient_id, 'message_text': m.message_text, 'timestamp': m.timestamp} for m in sent_messages]
    }
    return jsonify(messages), 200

# Create a discussion topic
@app.route('/discussion-topic', methods=['POST'])
@jwt_required()
def create_discussion_topic():
    data = request.get_json()
    topic_title = data.get('topic_title')
    description = data.get('description')

    if not topic_title or not description:
        return bad_request(_('Missing topic_title or description'))

    new_topic = DiscussionTopic(topic_title=topic_title, description=description)
    db.session.add(new_topic)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error creating discussion topic')}), 500

    return jsonify({'message': _('Discussion topic created successfully')}), 201

# Get all discussion topics
@app.route('/discussion-topics', methods=['GET'])
@jwt_required()
def get_discussion_topics():
    topics = DiscussionTopic.query.all()
    topic_list = [{'id': t.id, 'topic_title': t.topic_title, 'description': t.description, 'timestamp': t.timestamp} for t in topics]
    return jsonify(topic_list), 200

# Add a post to a discussion
@app.route('/discussion-post', methods=['POST'])
@jwt_required()
def add_discussion_post():
    data = request.get_json()
    topic_id = data.get('topic_id')
    post_content = data.get('post_content')

    if not topic_id or not post_content:
        return bad_request(_('Missing topic_id or post_content'))

    new_post = DiscussionPost(topic_id=topic_id, user_id=get_jwt_identity()['user_id'], post_content=post_content)
    db.session.add(new_post)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': _('Error adding discussion post')}), 500

    return jsonify({'message': _('Discussion post added successfully')}), 201

# Get all posts for a discussion topic
@app.route('/discussion-posts/<int:topic_id>', methods=['GET'])
@jwt_required()
def get_discussion_posts(topic_id):
    posts = DiscussionPost.query.filter_by(topic_id=topic_id).all()
    post_list = [{'id': p.id, 'user_id': p.user_id, 'post_content': p.post_content, 'timestamp': p.timestamp} for p in posts]
    return jsonify(post_list), 200

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

# Run the application
if __name__ == '__main__':
    socketio.run(app, debug=True)
