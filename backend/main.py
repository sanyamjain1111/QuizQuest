import os
from flask import Flask, jsonify, request
from application import config
from application.config import LocalDevelopementConfig
from application.database import db
from flask_cors import CORS
from flask_mail import Mail
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

# Initialize app components
app = None
mail = Mail()
# Initialize JWT Manager
jwt = JWTManager()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    app.secret_key = "jain1111"
    
    if os.getenv('ENV', "developement") == "production":
        raise Exception("Currently no production config is setup.")
    else:
        print("Starting Local Developement")
        app.config.from_object(LocalDevelopementConfig)
        db.init_app(app)
    app.app_context().push()
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db?timeout=30'
    app.config['SQLALCHEMY_ECHO'] = True
    os.makedirs('static/upload', exist_ok=True)
    app.config["UPLOAD_FOLDER"] = "static/upload"
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') 
    app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
     
    # Set up JWT configuration
    app.config['JWT_SECRET_KEY'] = 'jain1234'  # Change this to a secure random key
    jwt.init_app(app)
    mail.init_app(app)
 
    return app

# Create the application instance
app = create_app()

# Create all database tables
with app.app_context():
    db.create_all()

# Import controllers after app is created to avoid circular imports
from application.controllers import *

# Import and register the reminder blueprint
from application.reminder_routes import reminder_bp
if 'reminder' not in [bp.name for bp in app.blueprints.values()]:
    app.register_blueprint(reminder_bp)

# Enable CORS
CORS(app, supports_credentials=True)

# Initialize the scheduler (only once in production or when not in reloader)
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    from application.reminder_scheduler import setup_reminder_scheduler
    scheduler = setup_reminder_scheduler(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)