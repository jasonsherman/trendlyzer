from flask import Flask, request
import os
from keybert import KeyBERT
import spacy
from collections import Counter
from fpdf import FPDF

# Theme Mapping
theme_mapping = {
    'Lead Capture': ['email', 'phone', 'contact', 'address'],
    'Customer Support': ['assistance', 'support', 'help', 'question'],
    'AI Trust': ['ai', 'agent', 'human', 'real', 'bot'],
    'Sales Inquiry': ['price', 'cost', 'service', 'buy', 'purchase'],
    'Appointment Booking': ['appointment', 'schedule', 'meeting', 'consultation'],
}

# Known Companies and Locations
company_names = ['vengo', 'purrfect', 'vengana']
locations = ['serbia', 'usa', 'london',
             'canada', 'new york', 'germany', 'paris']

app = Flask(__name__)

# Set upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'txt'}

# Load SpaCy model once (important!)
nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def split_conversations(text):
    conversations = []
    current_convo = ""

    lines = text.splitlines()

    for line in lines:
        if line.startswith("Agent:") and current_convo:
            conversations.append(current_convo.strip())
            current_convo = line  # Start a new conversation
        else:
            current_convo += "\n" + line

    if current_convo:
        conversations.append(current_convo.strip())

    return conversations


def categorize_keyword(kw):
    kw_lower = kw.lower()
    if kw_lower in company_names:
        return 'Company name'
    elif kw_lower in locations:
        return 'Location'
    else:
        return kw


def generate_pdf_report(filename, mode, word_count, line_count, top_keywords, theme_counts):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Trendlyzer - Trend Analyzer & Insights Report",
             ln=True, align='C')

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Filename: {filename}", ln=True)
    pdf.cell(0, 10, f"Document Mode: {mode}", ln=True)
    pdf.cell(0, 10, f"Total Lines: {line_count}", ln=True)
    pdf.cell(0, 10, f"Total Words: {word_count}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Top Keywords", ln=True)

    pdf.set_font("Arial", "", 12)
    for kw, count in top_keywords:
        pdf.cell(0, 10, f"- {kw} ({count} mentions)", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Detected Themes", ln=True)

    pdf.set_font("Arial", "", 12)
    for theme, count in theme_counts.items():
        pdf.cell(0, 10, f"- {theme} ({count} mentions)", ln=True)

    # Save the PDF
    if not os.path.exists('static/reports'):
        os.makedirs('static/reports')

    report_path = os.path.join(
        'static/reports', f"{filename.replace('.txt', '')}_report.pdf")

    pdf.output(report_path)
    return report_path


@app.route('/')
def home():
    return '''
    <h1>Welcome to Trendlyzer! 🚀</h1>
    <p>Upload your file below:</p>
    <form method="post" action="/upload" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request.'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file.'

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        file_extension = file.filename.rsplit('.', 1)[1].lower()

        if file_extension == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            word_count = len(content.split())
            line_count = len(content.splitlines())

            # Check if document is conversational
            if content.count('Agent:') >= 5:
                conversations = split_conversations(content)
                mode = "Conversational Document"
            else:
                conversations = [content]
                mode = "Normal Document"

            # Analyze each conversation or the full text
            all_keywords = []

            for convo in conversations:
                keywords = kw_model.extract_keywords(convo, top_n=5)
                convo_keywords = [categorize_keyword(
                    kw) for kw, score in keywords]
                all_keywords.extend(convo_keywords)

            # Get top 10 keywords overall
            top_keywords = Counter(all_keywords).most_common(10)

            # Group keywords into Themes
            theme_counts = {}

            for kw, count in top_keywords:
                for theme, keywords in theme_mapping.items():
                    if kw.lower() in keywords:
                        theme_counts[theme] = theme_counts.get(
                            theme, 0) + count

            # Generate PDF report
            report_path = generate_pdf_report(
                file.filename, mode, word_count, line_count, top_keywords, theme_counts)

            return f'''
            <h2>File Uploaded and Analyzed ✅</h2>
            <p><b>Filename:</b> {file.filename}</p>
            <p><b>Mode:</b> {mode}</p>
            <p><b>Total Lines:</b> {line_count}</p>
            <p><b>Total Words:</b> {word_count}</p>
            <p><b>PDF Report Generated:</b> <a href="/{report_path}" target="_blank">Download Here</a></p>


            <h3>Top Keywords:</h3>
            <ul>
                {''.join(f'<li>{kw} ({count} mentions)</li>' for kw, count in top_keywords)}
            </ul>

            <h3>Detected Themes:</h3>
            <ul>
                {''.join(f'<li>{theme} ({count} mentions)</li>' for theme, count in theme_counts.items())}
            </ul>
            '''
        else:
            return f'File {file.filename} uploaded, but advanced analysis not yet available.'

    return 'Invalid file type. Allowed: PDF, DOCX, XLSX, TXT.'


if __name__ == '__main__':
    app.run(debug=True)
