from flask import Flask, request # request was imported for request path during retrieval of the user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os # os was import for the directory purposes of the document upload and storage

# Initialize SQLAlchemy for database operations
db = SQLAlchemy()

# Initialize Flask-Migrate for handling database migrations
migrate = Migrate()

# Initialize Flask-Login for managing user sessions and authentication
login_manager = LoginManager()

# Defining function for initialising the app or we can say for creating an instance of the app 
def initialize_app():
    app = Flask(__name__)
    # Configuration for the Flask app:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Set the database URI for SQLAlchemy to use SQLite and store data in app.db.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable SQLAlchemy's event tracking system to save memory and improve performance.
    app.config['SECRET_KEY'] = "SECRET_KEY"  # Define the secret key for securing sessions and cryptographic operations.

    # Configure upload folders
    app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static','uploads')  # Directory to store uploaded files
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize the Flask extensions with the Flask application instance:
    db.init_app(app)  # Link the SQLAlchemy database instance to the Flask app.
    migrate.init_app(app, db)  # Configure Flask-Migrate with the Flask app and SQLAlchemy database.
    login_manager.init_app(app)  # Set up Flask-Login for managing user authentication.

    # Specify the name for the page to redirect unauthorized users, in this case, it redirects to the Index (Home) page
    login_manager.login_view = 'main.index'

    # Import and register blueprints
    from .routes import main as main_routes
    app.register_blueprint(main_routes)
    from .api import api as api_routes
    api_routes.init_app(app)

    return app

# Setting up a way so that flask-login can retrive the users from the respective tables
""" Earlier I was just checking the id of the user from the username input, first it matched it in customer table, then professional and then 
admin but this created a problem becuase for example if a professional who id is 2 is trying to log in first the model check the id in customer
table but if there was a customer in the table with id 2 it will pick that customer with id 2 not the professional because it is checked later.
To solve thsi problem I found the perfect solution, the solution was that the function will check the path the user is on, if it is */professional/
it will only check the professional table and same for the rest.
"""
from app.models import Professional, Admin, Customer
""" The app.models import the tables, the reason i have written this code line below not with other imports because it was earlier causing
circular import loop as app import models and models import db from app to solve this i decided to do a lazy import means it will only imported
when it is used and at that time the other imports are already loaded.
"""
@login_manager.user_loader
def retrieve_user(user_id):

    path = request.path

    if path.startswith('/professional/'):
        user = Professional.query.get(int(user_id))
        if user:
            return user

    elif path.startswith('/customer/'):
        user = Customer.query.get(int(user_id))
        if user:
            return user

    elif path.startswith('/admin/'):
        user = Admin.query.get(int(user_id))
        if user:
            return user

    return None