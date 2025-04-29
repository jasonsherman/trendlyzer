from flask import Flask, request, render_template, url_for
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
        return 'company name'
    elif kw_lower in locations:
        return 'location'
    else:
        return kw


def generate_pdf_report(filename, mode, word_count, line_count, top_keywords, theme_counts, conversations, company_name):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    # Insert Logo at the Top
    logo_path = 'static/images/trendlyzer-report-logo.png'  # Make sure this exists!

    if os.path.exists(logo_path):
        # Adjust x, y, w for positioning
        pdf.image(logo_path, x=80, y=10, w=50)
        pdf.ln(30)  # Push content below logo
    else:
        pdf.ln(20)  # No logo fallback spacing
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 7, "Trend Analyzer & Insights Report",
             ln=True, align='C')

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)

    # Overview Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Set dark blue
    pdf.cell(0, 7, "Overview", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset text color back to black

    pdf.set_font("Arial", "", 12)

    overview = (
        f"This report was created for {company_name} as a {mode.lower()} "
        f"containing approximately {word_count:,} words and {line_count:,} lines. "
        f"The analysis identified top themes like {', '.join(list(theme_counts.keys())[:3])}."
    )
    pdf.multi_cell(0, 7, overview)
    pdf.ln(8)

    # Key Highlights Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Set dark blue
    pdf.cell(0, 7, "Key Highlights", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset text color back to black
    pdf.set_font("Arial", "", 12)

    total_conversations = len(conversations)
    email_conversion_rate = 77.55  # example %
    phone_conversion_rate = 57.65  # example %

    pdf.cell(
        0, 7, f"- Total Conversations Analyzed: {total_conversations}", ln=True)
    pdf.cell(
        0, 7, f"- Email Leads Collected: {email_conversion_rate}%", ln=True)
    pdf.cell(
        0, 7, f"- Phone Numbers Collected: {phone_conversion_rate}%", ln=True)
    pdf.ln(8)

    import matplotlib.pyplot as plt

    # Create a simple bar chart
    categories = ['Email Leads', 'Phone Numbers']
    values = [email_conversion_rate, phone_conversion_rate]

    plt.figure(figsize=(4, 3))
    plt.bar(categories, values)
    plt.title('Lead Capture Rates')
    plt.ylabel('Percentage (%)')
    plt.ylim(0, 100)

    # Save the chart
    chart_path = os.path.join(
        'static/reports', f"{filename.replace('.txt', '')}_chart.png")
    plt.savefig(chart_path)
    plt.close()

    # Insert the chart into PDF
    pdf.image(chart_path, w=100)
    pdf.ln(10)

    # Top 3 Lead Capture Metrics Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Set dark blue
    pdf.cell(0, 7, "Top 3 Lead Capture Metrics", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset text color back to black
    pdf.set_font("Arial", "", 12)

    follow_up_rate = 51  # example follow-up % from your original report

    pdf.cell(
        0, 7, f"- {email_conversion_rate}% of customers provided an email after chatting", ln=True)
    pdf.cell(
        0, 7, f"- {phone_conversion_rate}% of customers provided a phone number", ln=True)
    pdf.cell(
        0, 7, f"- Over {follow_up_rate}% of all conversations led to actionable follow-ups", ln=True)
    pdf.ln(8)

    # Chart for Lead Capture Metrics
    categories = ['Email Provided', 'Phone Provided', 'Follow-Ups']
    values = [email_conversion_rate, phone_conversion_rate, follow_up_rate]

    plt.figure(figsize=(4.5, 3))
    plt.barh(categories, values, color='#4d6df3')
    plt.xlabel('Percentage')
    plt.title('Top Lead Capture Metrics')
    plt.xlim(0, 100)

    lead_chart_path = os.path.join(
        'static/reports', f"{filename.replace('.txt', '')}_lead_metrics.png")
    plt.savefig(lead_chart_path, bbox_inches='tight')
    plt.close()

    pdf.image(lead_chart_path, w=110)
    pdf.ln(10)

    # Top Keywords Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Set dark blue
    pdf.cell(0, 7, "Top Keywords", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset text color back to black
    pdf.set_font("Arial", "", 12)
    for kw, count in top_keywords:
        pdf.cell(0, 7, f"- {kw} ({count} mentions)", ln=True)
    pdf.ln(8)

    # Detected Themes Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Set dark blue
    pdf.cell(0, 7, "Detected Themes", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset text color back to black
    pdf.set_font("Arial", "", 12)
    for theme, count in theme_counts.items():
        pdf.cell(0, 7, f"- {theme} ({count} mentions)", ln=True)
    pdf.ln(8)

    # Common Themes in Conversations Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Set dark blue
    pdf.cell(0, 7, "Common Themes in Conversations", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset text color back to black
    pdf.set_font("Arial", "", 12)

    common_themes = [
        "Request Service Information: Detailed questions about services, pricing, timelines, and processes.",
        "Initiate Sales Inquiries: Many customers express interest in purchasing or getting started.",
        "Seek Customer Support: Some customers come with support-related questions, often post-sale.",
        "Schedule Appointments or Demos: Agents were frequently asked how to book consultations or services.",
        "Verify Business Credibility: Visitors often ask if the company is real, legitimate, or human-operated.",
        "Location and Availability: Customers ask where the business operates or if service is available in their area."
    ]

    for theme in common_themes:
        pdf.multi_cell(0, 7, f"- {theme}")
        pdf.ln(1)

    pdf.ln(8)

    # Top Keywords and Conversation Drivers Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Set dark blue
    pdf.cell(0, 7, "Top Keywords and Conversation Drivers", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset text color back to black
    pdf.set_font("Arial", "", 12)

    # Short paragraph explanation
    keyword_intro = (
        "Analyzing word frequency provides insight into what customers care about most. "
        "These keywords reveal user intents, buying readiness, and support needs."
    )
    pdf.multi_cell(0, 7, keyword_intro)
    pdf.ln(5)

    # List top keywords again (nicely)
    for kw, count in top_keywords:
        pdf.cell(0, 7, f"- {kw} ({count} mentions)", ln=True)

    pdf.ln(8)

    # Trends & Impact on Businesses Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Set dark blue
    pdf.cell(0, 7, "Trends & Impact on Businesses", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset text color back to black
    pdf.set_font("Arial", "", 12)

    trends = [
        "Higher Lead Volume: Businesses using AI agents are collecting contact information in ~78% of conversations, significantly above the industry average.",
        "Customer Readiness: Nearly half of conversations involved direct requests to speak to a human or book services, showing strong buying intent.",
        "Trust Signals Matter: Many customers questioned whether the AI agent was real or human, highlighting the need for credibility-building in conversations."
    ]

    for trend in trends:
        pdf.multi_cell(0, 7, f"- {trend}")
        pdf.ln(1)

    pdf.ln(8)

    # Create the Trends Impact Chart
    from matplotlib import pyplot as plt

    chart_path = 'static/reports/trends_impact_chart.png'
    categories = ['Lead Capture Success',
                  'Customer Readiness', 'Trust Concerns']
    percentages = [78, 49, 36]
    colors = ['#4CAF50', '#2196F3', '#FF9800']

    plt.figure(figsize=(6, 4))
    bars = plt.bar(categories, percentages, color=colors)

    for bar, pct in zip(bars, percentages):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                 f'{pct}%', ha='center', fontsize=10, fontweight='bold')

    plt.title('Business Trends Observed in AI Conversations')
    plt.ylabel('Percentage')
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    # Add chart image to PDF
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Dark blue for heading
    pdf.cell(0, 7, "Visual Insights", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset back to black text

    pdf.image(chart_path, w=100)  # Insert the chart
    pdf.ln(10)  # Add some spacing after the chart

    # Sales Insights & Strategies Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Set dark blue
    pdf.cell(0, 7, "Sales Insights & Strategies", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset text color back to black
    pdf.set_font("Arial", "", 12)

    sales_insights = [
        "AI agents are effectively pre-qualifying leads by gathering needs, budget information, and location details.",
        "Teams can intervene only when necessary, saving significant time and resources while maintaining engagement quality.",
        "Businesses can leverage the data gathered during chats to personalize follow-up outreach and improve closing rates."
    ]

    for insight in sales_insights:
        pdf.multi_cell(0, 7, f"- {insight}")
        pdf.ln(1)

    pdf.ln(8)

    # Recommendations Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(44, 82, 145)  # Set dark blue
    pdf.cell(0, 7, "Recommendations", ln=True)
    pdf.set_text_color(0, 0, 0)  # Reset text color back to black
    pdf.set_font("Arial", "", 12)

    recommendations = [
        "Add clear Call-to-Actions (CTAs) to AI flows (e.g., 'Would you like a team member to reach out?') to increase lead capture rates.",
        "Personalize follow-up emails using data collected during AI conversations for higher engagement.",
        "Refine agent scripts by focusing on top keywords and conversation intents to streamline answers and boost customer trust."
    ]

    for rec in recommendations:
        pdf.multi_cell(0, 7, f"- {rec}")
        pdf.ln(1)

    pdf.ln(8)

    # Footer (should be the LAST thing before output)
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, 'Generated by Trendlyzer | VengoAI.com', 0, 1, 'C')

    # Save Report
    if not os.path.exists('static/reports'):
        os.makedirs('static/reports')

    report_filename = f"{filename.replace('.txt', '')}_report.pdf"
    report_path = os.path.join(
        'static/reports', report_filename).replace("\\", "/")
    pdf.output(report_path)

    return report_path, overview


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request.'

    file = request.files['file']
    company_name = request.form.get(
        'company_name', 'Your Company Name or Full Name')

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
                report_path, overview = generate_pdf_report(
                    file.filename, mode, word_count, line_count, top_keywords, theme_counts, conversations, company_name)

            return render_template('results.html',
                                   company_name=company_name,
                                   overview=overview,
                                   top_keywords=top_keywords,
                                   theme_counts=theme_counts,
                                   report_path=report_path)

        # If the file was allowed but not TXT or TXT failed to process
        return f'File {file.filename} uploaded, but advanced analysis not yet available.'

    # If file extension not allowed
    return 'Invalid file type. Allowed: PDF, DOCX, XLSX, TXT.'


if __name__ == '__main__':
    app.run(debug=True)
