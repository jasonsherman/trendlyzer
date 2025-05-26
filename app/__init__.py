"""
Application factory for the Trendlyzer application.
"""
import os
import logging
from flask import Flask
from flask_mail import Mail
from .config.config import FLASK_CONFIG, MAIL_CONFIG

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    app.config.update(FLASK_CONFIG)
    
    # Configure mail settings
    app.config.update({
        'MAIL_SERVER': 'smtp.gmail.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': os.getenv('MAIL_USERNAME')
    })
    
    # Initialize extensions
    mail = Mail(app)
    app.mail = mail  # Store mail instance in app context
    
    # Register blueprints
    from .routes.main import main
    app.register_blueprint(main)
    
    # Create required directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app 