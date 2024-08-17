# Intelligent Math Tutor

An intelligent tutoring system that provides personalized math problem-solving assistance. The system adapts to the user's performance and provides detailed feedback and hints for each problem. The application includes user authentication, progress tracking, and an interactive problem-solving interface.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Contributing](#contributing)
- [Deployment](#deployment)
- [License](#license)

## Features

- **User Authentication:** Secure user registration and login with JWT.
- **Adaptive Learning:** Recommends problems based on user performance.
- **Detailed Feedback:** Provides detailed feedback and hints for each problem.
- **Progress Tracking:** Tracks user progress and displays performance metrics.
- **Interactive Interface:** User-friendly interface for solving math problems.
- **User Feedback:** Allows users to submit feedback about the application.
- **User Analytics:** Provides analytics data on user performance and feedback.
- **Badges and Rewards:** Users earn badges for their achievements.
- **Notifications:** Users receive notifications about their progress and other updates.
- **Social Sharing:** Users can share their achievements on social media.
- **Interactive Whiteboard:** Real-time collaborative whiteboard for problem-solving.
- **Video Tutorials:** Integration of video tutorials for complex problem explanations.
- **Custom Problem Sets:** Users can create and share custom problem sets.
- **Gamification:** Point system and leaderboards to enhance engagement.

## Tech Stack

- **Frontend:**
  - React
  - Axios
  - CSS

- **Backend:**
  - Flask
  - SQLAlchemy
  - Flask-JWT-Extended
  - Flask-Bcrypt
  - Flask-Migrate
  - Flask-Babel
  - Flask-Limiter
  - Flask-SocketIO

- **Database:**
  - SQLite (for simplicity, can be replaced with any SQL database)

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js and npm

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/IntelligentMathTutor.git
   cd IntelligentMathTutor/backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Run the Flask application:**
   ```bash
   flask run
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend/math-tutor
   ```

2. **Install the required dependencies:**
   ```bash
   npm install
   ```

3. **Start the React application:**
   ```bash
   npm start
   ```

## Usage

1. **Register a new user:**
   - Open the application in your browser at `http://localhost:3000`
   - Fill in the registration form and submit

2. **Login with the registered user:**
   - Enter the registered email and password
   - Submit the login form

3. **Solve recommended problems:**
   - Follow the interactive interface to solve problems
   - Receive detailed feedback and hints

4. **Track progress:**
   - View your progress and performance metrics

5. **Submit feedback:**
   - Use the feedback form to submit your feedback about the application

6. **View analytics:**
   - Access the analytics dashboard to view your performance metrics and feedback count

7. **View badges:**
   - Check the badges you have earned for your achievements

8. **Read notifications:**
   - Stay updated with notifications about your progress and other updates

9. **Share achievements:**
   - Share your achievements on social media platforms

10. **Use the interactive whiteboard:**
    - Collaborate in real-time using the interactive whiteboard

11. **Watch video tutorials:**
    - Access video tutorials for complex problem explanations

12. **Create and share custom problem sets:**
    - Create and share your own problem sets with others

13. **Check the leaderboard:**
    - View the leaderboard to see your ranking and earn points for solving problems

## API Endpoints

### Authentication

- **Register:** `POST /register`
  - Request Body: `{ "username": "your_username", "email": "your_email", "password": "your_password" }`
  - Response: `{ "message": "User registered successfully" }`

- **Login:** `POST /login`
  - Request Body: `{ "email": "your_email", "password": "your_password" }`
  - Response: `{ "access_token": "your_jwt_token" }`

### Problem Solving

- **Recommend Problem:** `GET /recommend/<int:user_id>`
  - Response: `{ "problem_id": 1, "question": "2+2", "difficulty": "easy", "feedback": "Basic addition problem" }`

- **Track Progress:** `POST /progress`
  - Request Body: `{ "user_id": 1, "problem_id": 1, "status": "completed" }`
  - Response: `{ "message": "Progress tracked successfully" }`

- **Get Progress:** `GET /progress/<int:user_id>`
  - Response: `[ { "problem_id": 1, "status": "completed", "timestamp": "2023-01-01T00:00:00" }, ... ]`

### User Profile

- **Get Profile:** `GET /profile`
  - Response: `{ "username": "your_username", "email": "your_email" }`

- **Update Profile:** `PUT /profile`
  - Request Body: `{ "username": "new_username", "email": "new_email" }`
  - Response: `{ "message": "Profile updated successfully" }`

### Dashboard

- **Get Dashboard:** `GET /dashboard`
  - Response: `{ "username": "your_username", "email": "your_email", "total_problems": 10, "correct_answers": 8, "incorrect_answers": 2, "performance_ratio": 0.8 }`

### Feedback

- **Submit Feedback:** `POST /feedback`
  - Request Body: `{ "feedback": "your_feedback" }`
  - Response: `{ "message": "Feedback submitted successfully" }`

### Analytics

- **Get Analytics:** `GET /analytics`
  - Response: `{ "username": "your_username", "email": "your_email", "total_problems": 10, "correct_answers": 8, "incorrect_answers": 2, "performance_ratio": 0.8, "feedback_count": 5 }`

### Badges

- **Get Badges:** `GET /badges`
  - Response: `[ { "name": "First Solve", "description": "Completed first problem", "date_awarded": "2023-01-01T00:00:00" }, ... ]`

- **Award Badge:** `POST /award_badge`
  - Request Body: `{ "name": "Badge Name", "description": "Badge description" }`
  - Response: `{ "message": "Badge awarded successfully" }`

### Notifications

- **Get Notifications:** `GET /notifications`
  - Response: `[ { "message": "You completed a problem!", "date_sent": "2023-01-01T00:00:00", "is_read": false }, ... ]`

- **Send Notification:** `POST /notifications`
  - Request Body: `{ "message": "Notification message" }`
  - Response: `{ "message": "Notification sent successfully" }`

- **Mark Notification as Read:** `POST /notifications/read/<int:id>`
  - Response: `{ "message": "Notification marked as read" }`

### Whiteboard

- **Join Whiteboard Session:** `POST /whiteboard/join`
  - Request Body: `{ "room": "room_name", "username": "user_name" }`
  - Response: `{ "message": "Joined whiteboard session" }`

- **Leave Whiteboard Session:** `POST /whiteboard/leave`
  - Request Body: `{ "room": "room_name", "username": "user_name" }`
  - Response: `{ "message": "Left whiteboard session" }`

- **Draw on Whiteboard:** `POST /whiteboard/draw`
  - Request Body: `{ "room": "room_name", "drawData": { "x0": 0, "y0": 0, "x1": 1, "y1": 1 } }`
  - Response: `{ "message": "Drawing sent" }`

### Tutorials

- **Get Tutorials:** `GET /tutorials`
  - Response: `[ { "id": 1, "title": "Addition Tutorial", "content": "Video URL or Text Content", "problem_id": 1, "date_created": "2023-01-01T00:00:00" }, ... ]`

- **Add Tutorial:** `POST /tutorials`
  - Request Body: `{

 "title": "New Tutorial", "content": "Video URL or Text Content", "problem_id": 1 }`
  - Response: `{ "message": "Tutorial added successfully" }`

- **Get Tutorial:** `GET /tutorials/<int:id>`
  - Response: `{ "id": 1, "title": "Addition Tutorial", "content": "Video URL or Text Content", "problem_id": 1, "date_created": "2023-01-01T00:00:00" }`

### Learning Path

- **Get Learning Path:** `GET /learning_path/<int:user_id>`
  - Response: `{ "user_id": 1, "problems": "1,2,3", "date_created": "2023-01-01T00:00:00" }`

- **Create/Update Learning Path:** `POST /learning_path`
  - Request Body: `{ "user_id": 1, "problems": "1,2,3" }`
  - Response: `{ "message": "Learning path saved successfully" }`

## Testing

### Backend Tests

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Run the tests:**
   ```bash
   pytest
   ```

### Frontend Tests

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend/math-tutor
   ```

2. **Run the tests:**
   ```bash
   npm test
   ```

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

## Deployment

### Backend Deployment

1. **Configure Environment Variables:**
   - Create a `.env` file in the `backend` directory with the following content:
     ```plaintext
     FLASK_APP=app.py
     FLASK_ENV=production
     SQLALCHEMY_DATABASE_URI=postgresql://username:password@hostname:port/database
     SECRET_KEY=your_secret_key
     JWT_SECRET_KEY=your_jwt_secret_key
     ```

2. **Set Up PostgreSQL Database:**
   - Create a PostgreSQL database using a service like Heroku, AWS RDS, or a local PostgreSQL server.
   - Update the `.env` file with the PostgreSQL connection details.

3. **Run Database Migrations:**
   ```bash
   flask db upgrade
   ```

4. **Deploy to Heroku:**
   ```bash
   heroku create
   git add .
   git commit -m "Prepare for Heroku deployment"
   git push heroku main
   heroku run flask db upgrade
   ```

### Frontend Deployment

1. **Build the React Application:**
   ```bash
   npm run build
   ```

2. **Deploy to Vercel:**
   ```bash
   npm install -g vercel
   vercel
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
