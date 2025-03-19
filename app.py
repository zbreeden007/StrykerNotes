import os
from flask import Flask
from config import Config
from models import db
from routes import register_blueprints
from flask_migrate import Migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register all blueprints
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()

    # Add this after creating your app and initializing db
    migrate = Migrate(app, db)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)