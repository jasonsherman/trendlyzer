"""
Application factory for the Trendlyzer application.
"""
import os
import logging
from flask import Flask
from flask_mail import Mail
import spacy
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
    
    # Load NLP models
    try:
        try:
            nlp = spacy.load("en_core_web_md")
            logging.info("Loaded spaCy model: en_core_web_md (with word vectors)")
        except Exception as e:
            logging.warning(
                "Could not load en_core_web_md, falling back to en_core_web_sm. Similarity may be less accurate.")
            nlp = spacy.load("en_core_web_sm")
            logging.info("Loaded spaCy model: en_core_web_sm (no word vectors)")
        logging.info("NLP models loaded successfully")
    except Exception as e:
        logging.error(f"Error loading NLP models: {e}")
        raise
    
    app.nlp = nlp  # Store nlp instance in app context
    
    # Register blueprints
    from .routes.main import main
    app.register_blueprint(main)
    
    # Create required directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app 