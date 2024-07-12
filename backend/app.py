# Importing Flask from the flask package to create a Flask application
from flask import Flask

# Creating a Flask application instance
app = Flask(__name__)

# Defining a route for the home page
@app.route('/')
def home():
    """
    The home function returns a welcome message.
    This function is mapped to the '/' URL path.
    """
    return "Welcome to the Intelligent Math Tutor!"

# Checking if the script is executed directly and not imported
if __name__ == '__main__':
    # Running the Flask application in debug mode
    app.run(debug=True)
