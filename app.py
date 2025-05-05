from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from report_generator import ReportGenerator, ReportMetrics
from keyword_extractor import KeywordExtractor
from theme_analyzer import ThemeAnalyzer
from document_processor import DocumentProcessor
from metrics_calculator import MetricsCalculator
from email_sender import EmailSender
from dotenv import load_dotenv
from collections import Counter
import re
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv', 'md', 'rtf', 'ppt', 'pptx'}

THEME_MAPPING = {
    'Lead Capture': ['email', 'phone', 'contact', 'address'],
    'Customer Support': ['assistance', 'support', 'help', 'question'],
    'AI Trust': ['ai', 'agent', 'human', 'real', 'bot'],
    'Sales Inquiry': ['price', 'cost', 'service', 'buy', 'purchase'],
    'Appointment Booking': ['appointment', 'schedule', 'meeting', 'consultation'],
}

# Initialize the keyword extractor
kw = KeywordExtractor()

# Initialize the theme analyzer
theme_analyzer = ThemeAnalyzer()

# Initialize the document processor
doc_processor = DocumentProcessor()

# Initialize the metrics calculator
metrics_calc = MetricsCalculator()

# Initialize the email sender with environment variables
email_sender = EmailSender(
    smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    smtp_port=int(os.getenv('SMTP_PORT', '587')),
    username=os.getenv('SMTP_USERNAME', ''),
    password=os.getenv('SMTP_PASSWORD', '')
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in app.config['ALLOWED_EXTENSIONS']


def split_conversations(text):
    """Split text into conversations based on speaker patterns."""
    conversations = []
    current_conversation = ""
    lines = text.splitlines()

    for line in lines:
        if re.match(r"[^:]{1,40}:", line):  # If line contains a speaker
            if current_conversation:
                conversations.append(current_conversation.strip())
            current_conversation = line
        else:
            current_conversation += "\n" + line

    if current_conversation:
        conversations.append(current_conversation.strip())

    return conversations


def categorize_keyword(keyword):
    """Categorize a keyword into a theme."""
    keyword = keyword.lower()
    for theme, keywords in THEME_MAPPING.items():
        if keyword in keywords:
            return theme
    return "Other"


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    global kw
    """API endpoint for programmatic document analysis.

    Accepts:
    - file: Document file (PDF, DOCX, XLS, TXT, etc.)
    - company_name: Optional company name for the report

    Returns:
    JSON response with:
    - report_url: URL to download the generated PDF report
    - overview: Text overview of the analysis
    - top_keywords: List of top keywords and their frequencies
    - theme_counts: Count of themes detected
    - metrics: Various analysis metrics
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    company_name = request.form.get('company_name', 'Your Company Name')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        file_extension = filename.rsplit('.', 1)[1].lower()

        # Process the file
        content = doc_processor.process_document(filepath)
        if content is None:
            return jsonify({'error': 'Could not process file content'}), 400

        # Analyze the content
        word_count = len(content.split())
        line_count = len(content.splitlines())
        lines = [line.rstrip("\n") for line in content.splitlines()]

        # Detect document mode
        has_agent = any(re.match(r"Agent:", line) for line in lines)
        has_other_speaker = any(re.match(
            r"[^:]{1,40}:", line) and not line.startswith("Agent:") for line in lines)
        mode = "Conversational Document" if has_agent and has_other_speaker else "Normal Document"

        # Process conversations and extract metrics
        conversations = split_conversations(content)
        conv_data = []
        all_keywords = []

        for conv in conversations:
            keywords = kw.extract_keywords(conv, top_n=5)
            convo_keywords = [categorize_keyword(kw) for kw, _ in keywords]
            all_keywords.extend(convo_keywords)

        top_keywords = Counter(all_keywords).most_common(10)
        theme_counts = {}
        for kw, count in top_keywords:
            for theme, keywords in THEME_MAPPING.items():
                if kw.lower() in keywords:
                    theme_counts[theme] = theme_counts.get(theme, 0) + count

        # Generate metrics
        metrics = metrics_calc.calculate_metrics(content)

        # Generate the report
        report_generator = ReportGenerator(filename, company_name)
        report_path, overview = report_generator.generate(
            mode=mode,
            metrics=ReportMetrics(**metrics),
            top_keywords=top_keywords,
            theme_counts=theme_counts,
            conversations=conversations,
            full_text=content
        )

        # Send email notification if configured
        if os.getenv('SMTP_USERNAME') and os.getenv('SMTP_PASSWORD'):
            try:
                email_sender.send_report(
                    os.getenv('RECEIVER_MAIL'), report_path, company_name)
            except Exception as e:
                logger.warning(f"Failed to send email: {e}")

        # Return the results
        return jsonify({
            'report_url': request.host_url.rstrip('/') + report_path,
            'overview': overview,
            'top_keywords': top_keywords,
            'theme_counts': theme_counts,
            'metrics': metrics
        })

    except Exception as e:
        logger.error(f"Error in API analysis: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/test-api')
def test_api():
    """Render the API test page."""
    return render_template('test_api.html')

# ... existing code ...


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static/reports', exist_ok=True)

    # Run the Flask application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
