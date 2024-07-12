from backend.app import db

# User model to store user information
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each user
    username = db.Column(db.String(150), unique=True, nullable=False)  # Username, must be unique
    email = db.Column(db.String(150), unique=True, nullable=False)  # Email, must be unique
    password = db.Column(db.String(256), nullable=False)  # Hashed password

# Progress model to track user progress on problems
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each progress entry
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User model
    problem_id = db.Column(db.Integer, nullable=False)  # Identifier for the problem
    status = db.Column(db.String(50), nullable=False)  # Status of the problem (e.g., 'completed', 'in-progress')
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Timestamp of when the progress was tracked
