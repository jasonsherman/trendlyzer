"""
Configuration settings for the Trendlyzer application.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'static/reports'
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx',
    'txt', 'csv', 'md', 'rtf', 'ppt', 'pptx'
}

# Report Configuration
REPORT_CONFIG = {
    'font': {
        'name': 'DejaVu',
        'regular': 'app/static/fonts/DejaVuSans.ttf',
        'bold': 'app/static/fonts/DejaVuSans-Bold.ttf',
        'italic': 'app/static/fonts/DejaVuSans-Oblique.ttf'
    },
    'colors': {
        'primary': (44, 82, 145),  # Dark blue
        'secondary': (77, 109, 243),  # Light blue
        'success': (76, 175, 80),  # Green
        'warning': (255, 152, 0),  # Orange
    },
    'charts': {
        'default_size': (4, 3),
        'bar_color': '#4d6df3',
        'max_percentage': 100
    }
}

# Theme Mapping
THEME_MAPPING = {
    'Lead Capture': ['email', 'phone', 'contact', 'address'],
    'Customer Support': ['assistance', 'support', 'help', 'question'],
    'AI Trust': ['ai', 'agent', 'human', 'real', 'bot'],
    'Sales Inquiry': ['price', 'cost', 'service', 'buy', 'purchase'],
    'Appointment Booking': ['appointment', 'schedule', 'meeting', 'consultation'],
}

# Known Companies and Locations
COMPANY_NAMES = ['vengo', 'purrfect', 'vengana']
LOCATIONS = [
    'serbia', 'usa', 'london', 'canada',
    'new york', 'germany', 'paris'
]

# Email Configuration
MAIL_CONFIG = {
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': os.getenv("MAIL_USERNAME"),
    'MAIL_PASSWORD': os.getenv("MAIL_PASSWORD"),
    'MAIL_DEFAULT_SENDER': os.getenv("MAIL_USERNAME")
}

# Flask App Configuration
FLASK_CONFIG = {
    'SECRET_KEY': 'your_secret_key_here',
    'UPLOAD_FOLDER': UPLOAD_FOLDER
} 