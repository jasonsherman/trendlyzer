import os
import PyPDF2
import docx
import pandas as pd
import re


class DocumentProcessor:
    def __init__(self):
        self.supported_extensions = {
            '.pdf': self._read_pdf,
            '.docx': self._read_docx,
            '.doc': self._read_docx,
            '.xlsx': self._read_excel,
            '.xls': self._read_excel,
            '.txt': self._read_text,
            '.csv': self._read_csv,
            '.md': self._read_text,
            '.rtf': self._read_text,
            '.ppt': self._read_text,
            '.pptx': self._read_text
        }

    def process_document(self, file_path):
        """
        Process a document and extract its text content

        Args:
            file_path (str): Path to the document file

        Returns:
            str: Extracted text content
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {ext}")

        return self.supported_extensions[ext](file_path)

    def _read_pdf(self, file_path):
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def _read_docx(self, file_path):
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def _read_excel(self, file_path):
        """Extract text from Excel file"""
        df = pd.read_excel(file_path)
        return df.to_string()

    def _read_text(self, file_path):
        """Extract text from text-based files"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _read_csv(self, file_path):
        """Extract text from CSV file"""
        df = pd.read_csv(file_path)
        return df.to_string()
