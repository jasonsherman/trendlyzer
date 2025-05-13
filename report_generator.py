from dataclasses import dataclass
from fpdf import FPDF
import os
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
from ai_analyzer import AIAnalyzer
import json
from theme_analyzer import ThemeAnalyzer


@dataclass
class ReportMetrics:
    word_count: int
    line_count: int
    total_conversations: int
    mode: str
    document_type: str = "Unknown"


class ReportGenerator:
    def __init__(self, filename, company_name):
        self.filename = filename
        self.company_name = company_name
        self.reports_dir = 'static/reports'
        self.ai_analyzer = AIAnalyzer()
        self.theme_analyzer = ThemeAnalyzer()
        os.makedirs(self.reports_dir, exist_ok=True)

    def _create_chart(self, data, title, chart_type='bar'):
        """Create a chart and return it as base64 string"""
        plt.figure(figsize=(10, 6))

        if chart_type == 'bar':
            plt.bar(data.keys(), data.values())
        elif chart_type == 'pie':
            plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
        elif chart_type == 'line':
            plt.plot(list(data.keys()), list(data.values()))

        plt.title(title)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save to bytes
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)
        plt.close()

        return base64.b64encode(img_data.getvalue()).decode()

    def generate(self, mode, metrics, top_keywords, theme_counts, conversations, full_text):
        """Generate a PDF report with AI-powered analysis results."""
        # Get AI analysis
        doc_type = self._detect_document_type(full_text)
        ai_analysis = self.ai_analyzer.analyze_document(full_text, doc_type)
        report_sections = self.ai_analyzer.generate_report_sections(
            full_text, doc_type)
        visualization_suggestions = self.ai_analyzer.suggest_visualizations(
            full_text, doc_type)

        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Set font
        pdf.set_font("Arial", "B", 16)

        # Add title
        pdf.cell(
            0, 10, f"Trendlyzer Report for {self.company_name}", ln=True, align='C')
        pdf.ln(10)

        # Add date and document type
        pdf.set_font("Arial", "", 12)
        pdf.cell(
            0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(0, 10, f"Document Type: {doc_type}", ln=True)
        pdf.ln(10)

        # Add Executive Summary
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Executive Summary", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, report_sections.get('executive_summary', ''))
        pdf.ln(10)

        # Add Key Findings
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Key Findings", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, report_sections.get('key_findings', ''))
        pdf.ln(10)

        # Add Document Metrics
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Document Metrics", ln=True)
        pdf.set_font("Arial", "", 12)
        metrics_text = f"Word Count: {metrics.word_count}\n"
        metrics_text += f"Line Count: {metrics.line_count}\n"
        if mode == "Conversational Document":
            metrics_text += f"Total Conversations: {metrics.total_conversations}\n"
        pdf.multi_cell(0, 10, metrics_text)
        pdf.ln(10)

        # Add Key Topics
        if 'key_topics' in ai_analysis:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Key Topics", ln=True)
            pdf.set_font("Arial", "", 12)
            topics_text = ", ".join(ai_analysis['key_topics'])
            pdf.multi_cell(0, 10, topics_text)
            pdf.ln(10)

        # Add Theme Analysis with Details
        theme_details = self.theme_analyzer.get_theme_details()
        if theme_details:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Theme Analysis", ln=True)
            pdf.set_font("Arial", "", 12)

            for theme in theme_details:
                # Theme name and count
                pdf.set_font("Arial", "B", 12)
                pdf.cell(
                    0, 10, f"{theme['name']} ({theme['count']} mentions)", ln=True)

                # Theme description
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(0, 10, theme['description'])

                # Key phrases
                pdf.set_font("Arial", "I", 10)
                phrases_text = "Key phrases: " + \
                    ", ".join(theme['key_phrases'])
                pdf.multi_cell(0, 10, phrases_text)
                pdf.ln(5)

        # Add Visualizations
        if visualization_suggestions:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Data Visualizations", ln=True)
            pdf.set_font("Arial", "", 12)

            for viz in visualization_suggestions:
                # Create and add chart
                chart_data = self._prepare_chart_data(viz['data_points'])
                chart_base64 = self._create_chart(
                    chart_data, viz['title'], viz['type'])

                # Add chart to PDF
                pdf.image(io.BytesIO(base64.b64decode(
                    chart_base64)), x=10, w=190)
                pdf.ln(10)

                # Add chart description
                pdf.set_font("Arial", "I", 10)
                pdf.multi_cell(0, 10, viz['purpose'])
                pdf.ln(5)

        # Add Detailed Analysis
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Detailed Analysis", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, report_sections.get('detailed_analysis', ''))
        pdf.ln(10)

        # Add Recommendations
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Recommendations", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, report_sections.get('recommendations', ''))
        pdf.ln(10)

        # Add Conclusion
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Conclusion", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, report_sections.get('conclusion', ''))
        pdf.ln(10)

        # Save the report
        report_filename = f"{self.filename}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        report_path = os.path.join(self.reports_dir, report_filename)
        pdf.output(report_path)

        # Return the report path and overview
        return f"/static/reports/{report_filename}", report_sections.get('executive_summary', '')

    def _detect_document_type(self, content: str) -> str:
        """Detect the type of document based on content"""
        # Simple heuristic-based detection
        content_lower = content.lower()

        if any(word in content_lower for word in ['invoice', 'payment', 'due', 'amount']):
            return "Invoice"
        elif any(word in content_lower for word in ['quarterly', 'annual', 'revenue', 'profit']):
            return "Financial Report"
        elif any(word in content_lower for word in ['slide', 'presentation', 'powerpoint']):
            return "Presentation"
        elif any(word in content_lower for word in ['agent:', 'customer:', 'support:']):
            return "Chat Transcript"
        elif any(word in content_lower for word in ['sales', 'revenue', 'target', 'quota']):
            return "Sales Report"
        else:
            return "General Document"

    def _prepare_chart_data(self, data_points: list) -> dict:
        """Prepare data for chart visualization"""
        # This is a simple implementation - you might want to enhance this
        # based on your specific data structure
        return {point: 1 for point in data_points}
