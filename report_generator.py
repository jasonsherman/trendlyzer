from dataclasses import dataclass
from fpdf import FPDF
import os
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64


@dataclass
class ReportMetrics:
    word_count: int
    line_count: int
    total_conversations: int
    mode: str


class ReportGenerator:
    def __init__(self, filename, company_name):
        self.filename = filename
        self.company_name = company_name
        self.reports_dir = 'static/reports'
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate(self, mode, metrics, top_keywords, theme_counts, conversations, full_text):
        """Generate a PDF report with analysis results."""
        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Set font
        pdf.set_font("Arial", "B", 16)

        # Add title
        pdf.cell(
            0, 10, f"Trendlyzer Report for {self.company_name}", ln=True, align='C')
        pdf.ln(10)

        # Add date
        pdf.set_font("Arial", "", 12)
        pdf.cell(
            0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(10)

        # Add overview
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Overview", ln=True)
        pdf.set_font("Arial", "", 12)
        overview = f"This report was generated for {self.company_name} as a {mode}. "
        overview += f"The document contains {metrics.word_count} words across {metrics.line_count} lines. "
        if mode == "Conversational Document":
            overview += f"There are {metrics.total_conversations} conversations analyzed."
        pdf.multi_cell(0, 10, overview)
        pdf.ln(10)

        # Add keywords
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Top Keywords", ln=True)
        pdf.set_font("Arial", "", 12)
        keywords_text = ", ".join(
            [f"{kw} ({count})" for kw, count in top_keywords])
        pdf.multi_cell(0, 10, keywords_text)
        pdf.ln(10)

        # Add themes
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Theme Analysis", ln=True)
        pdf.set_font("Arial", "", 12)
        for theme, count in theme_counts.items():
            pdf.cell(0, 10, f"{theme}: {count} occurrences", ln=True)
        pdf.ln(10)

        # Save the report
        report_filename = f"{self.filename}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        report_path = os.path.join(self.reports_dir, report_filename)
        pdf.output(report_path)

        # Return the report path and overview
        return f"/static/reports/{report_filename}", overview
