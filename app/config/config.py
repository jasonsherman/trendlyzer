"""
Configuration settings for the Trendlyzer application.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'app/static/reports'
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

AI_ANALYTICS_SCHEMA = {
        "document_type": "string (e.g. 'Chat Transcript', 'Financial Report')",
        "executive_summary": "string (≤120 words)",
        "sentiment": {
        "overall": "positive | neutral | negative",
        "confidence": "float (0.0 - 1.0)",
        "highlights": [
            {
            "text": "string (quoted source)",
            "sentiment": "positive | neutral | negative"
            }
        ]
        },
        "themes": [
            {
                "phrase": "string",
                "weight": "float (0.0 - 1.0)"
            }
        ],
        "key_topics": [
            {
                "topic": "string",
                "coverage_pct": "float (0.0 - 100.0)"
            }
        ],
        "detailed_analysis": [
            {
                "section_id": "string (e.g. 'S1')", 
                "heading": "string",
                "summary": "string",
                "source_pages": [ "int", "int" ]
            }
        ],
        "key_metrics": {
            "financial": [
                {
                "name": "string",
                "value": "float",
                "unit": "string",
                "period": "string"
                }
            ],
            "performance": [
                {
                    "name": "string",
                    "value": "float",
                    "unit": "string",
                    "period": "string"
                }
            ],
            "other_metrics": [
            {
                "name": "string",
                "value": "float",
                "unit": "string",
                "period": "string"
            }
    ]
        },
        "recommendations": [
            {
            "id": "string (e.g. 'R1')",
            "text": "string",
            "impact": "high | medium | low",
            "effort": "high | medium | low",
            "linked_section": "string (section_id)"
            }
        ],
        "visualizations": [
                    {
                    "id": "string (e.g., 'V1')",
                    "linked_metric": "string (metric name from key_metrics)",
                    "linked_section_id": "string (section_id from detailed_analysis, optional)",
                    "type": "string (e.g., 'line', 'bar', 'pie', 'table', 'heatmap', etc.)",
                    "title": "string (max 8 words, e.g., 'Quarterly Revenue Trend')",
                    "data_points": [
                        { "label": "string (category or x-axis label, e.g., 'Q1-2025')", "value": "number (y-axis value, e.g., 1200)" }
                    ],
                    "purpose": "string (max 20 words, describes the insight the visualization provides)",
                    "complexity": "string ('simple' or 'advanced', optional)",
                    "priority": "integer (1 = most important, optional)",
                    "recommended_chart_config": {
                        "x_axis": "string (label for X axis, if applicable)",
                        "y_axis": "string (label for Y axis, if applicable)",
                        "aggregation": "string (e.g., 'sum', 'average', optional)",
                        "note": "string (additional info for chart, optional)"
                    }
                    }
                ],
        "conclusion": "string"
}

prompt1_system = f"""
You are a senior business analyst. Respond only in JSON according to the provided JSON Schema. No prose.
{AI_ANALYTICS_SCHEMA}
"""

prompt1_user = """
 {{DOCUMENT_CONTENT}}

Instructions:
    - Analyze the document and fill all fields as specified.
    - For "visualizations", suggest up to 3 visualizations. For each, return the ACTUAL data points (labels and values) extracted from the document, so the visualization can be plotted directly from the JSON.
    - Do NOT return any prose, markdown, or explanation—just valid, minified JSON.
"""

prompt2_system = """
You are a data visualization expert. Based on the provided document analysis (key metrics and detailed analysis), suggest up to 3 high-impact charts or graphs using the exact JSON schema below. No explanations, no markdown—JSON ONLY.
"""
prompt2_user = """
Below is the structured summary of a document, including key metrics and detailed analysis.
---
 {{CALL1_OUTPUT}}
---
    
Based on this information, suggest up to 3 visualizations using the following JSON schema:

{
  "visualizations": [
    {
      "id": "string (e.g., 'V1')",
      "linked_metric": "string (metric name from key_metrics)",
      "linked_section_id": "string (section_id from detailed_analysis, optional)",
      "type": "string (e.g., 'line', 'bar', 'pie', 'table', 'heatmap', etc.)",
      "title": "string (max 8 words, e.g., 'Quarterly Revenue Trend')",
      "data_points": [
        "string (labels or categories shown on the chart, e.g., 'Q1-2025', 'Q2-2025')"
      ],
      "purpose": "string (max 20 words, describes the insight the visualization provides)",
      "complexity": "string ('simple' or 'advanced', optional)",
      "priority": "integer (1 = most important, optional)",
      "recommended_chart_config": {
        "x_axis": "string (label for X axis, if applicable)",
        "y_axis": "string (label for Y axis, if applicable)",
        "aggregation": "string (e.g., 'sum', 'average', optional)",
        "note": "string (additional info for chart, optional)"
      }
    }
  ]
}

Instructions:
- Select only the most meaningful visualizations, prioritizing trends, comparisons, or anomalies found in key metrics and analysis.
- Always fill in 'id', 'type', 'title', 'data_points', 'purpose', and 'linked_metric'.
- Other fields are optional but recommended.
- Respond with JSON ONLY. No markdown, no prose.
 """
