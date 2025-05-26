"""
Main routes for the Trendlyzer application.
"""
import os
import logging
from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, current_app
from werkzeug.utils import secure_filename
from ..config.config import (
    UPLOAD_FOLDER, ALLOWED_EXTENSIONS
)
from ..services.file_processor import process_file, allowed_file

from ..services.content_processor import process_content

logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    company_name = request.form.get('company_name', 'Company Name not provided')

    # Debug logging
    current_app.logger.info(f"Mail config: {current_app.config.get('MAIL_USERNAME')}")
    current_app.logger.info(f"Mail server: {current_app.config.get('MAIL_SERVER')}")
    current_app.logger.info(f"Mail port: {current_app.config.get('MAIL_PORT')}")

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            file_extension = filename.rsplit('.', 1)[1].lower()

            content = process_file(filepath, file_extension)
            if content is None:
                return jsonify({'error': 'Could not process file content'}), 400

            report_data = process_content(content, filename, company_name)
            
            # Store results in session
            session['results'] = {
                'company_name': company_name,
                'overview': report_data['overview'],

                'key_topics': report_data['key_topics'],
                'themes': report_data['themes'],

                'report_path': report_data['report_path']
            }
            
            
            return redirect(url_for('main.results_page'))

        except Exception as e:
            current_app.logger.error(f"Error in file analysis: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': f'Invalid file type. Allowed: {current_app.config["ALLOWED_EXTENSIONS"]}'}), 400

@main.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for programmatic document analysis."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    company_name = request.form.get('company_name', 'Company Name not provided')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)
            file_extension = filename.rsplit('.', 1)[1].lower()

            content = process_file(filepath, file_extension)
            if content is None:
                return jsonify({'error': 'Could not process file content'}), 400

            # Process the content and generate report
            report_data = process_content(content, filename, company_name)
            
            return jsonify({
                'report_url': request.host_url.rstrip('/') + report_data['report_path'],
                'company_name': company_name,
                'overview': report_data['overview'],

                'key_topics': report_data['key_topics'],
                'themes': report_data['themes'],

                'metrics': report_data['metrics']
            })

        except Exception as e:
            logger.error(f"Error in API analysis: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': f'Invalid file type. Allowed: {ALLOWED_EXTENSIONS}'}), 400

@main.route('/results')
def results_page():
    """Render the results page."""
    results = session.get('results')
    if not results:
        return redirect(url_for('main.home'))
    return render_template(
        'results.html',
        company_name=results['company_name'],
        overview=results['overview'],
        key_topics=results['key_topics'],
        themes=results['themes'],
        report_path=results['report_path']
    )
