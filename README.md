# 📄 Trendlyzer – AI-Driven Document Analyzer & Report Generator

Trendlyzer is a powerful document analysis tool that processes various file formats and generates comprehensive analytical reports with visualizations. It's particularly effective at analyzing conversational documents and business documents to extract meaningful insights.

## Features

---

## Installation

Trendlyzer is a lightweight microservice that allows users to upload files (PDF, DOCX, XLS, TXT), automatically extract and analyze their content, and generate a clean, professional PDF report filled with insights, trends, and visual charts.

Built with **privacy-first principles** — user files are automatically deleted after 24 hours.

---

## 💡 Why I Built This

Most businesses have valuable customer data locked inside documents.  
I wanted to create a **simple**, **open-source**, **AI-powered** tool that helps anyone — even non-technical users — automatically generate trend reports, improve decision-making, and respect data privacy.

---

## ⚙️ Key Features

- 📂 Upload and process multiple file types (PDF, DOCX, XLS, TXT)
- 🔍 NLP-driven keyword extraction and theme detection (SpaCy, KeyBERT)
- 📊 Generate visual charts (bar, pie, line)
- 📄 Create executive-style PDF reports (with insights and recommendations)
- 🛡️ No long-term storage: Files auto-delete after 24 hours
- 🌐 Easy integration with Supabase storage (free, open-source)

---

## 🛠️ Tech Stack

- **Backend**: Python (Flask)
- **Parsing**: pdfplumber, python-docx, pandas
- **NLP**: SpaCy, KeyBERT
- **Visualization**: matplotlib
- **PDF Generation**: fpdf2
- **Storage**: Supabase (temporary file storage)
- **Environment Management**: python-dotenv

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/jasonsherman/trendlyzer.git
cd trendlyzer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download required NLTK data:
```python
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

5. Download spaCy models:
```bash
python -m spacy download en_core_web_md
```

6. Create a `.env` file with the following variables:
```
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
RECEIVER_MAIL=recipient@example.com
```

## Usage

1. Start the application:
```bash
python run.py
```

2. Access the web interface at `http://localhost:5000`

3. Upload a document and provide a company name

4. View the generated report and analysis

### API Usage

Send a POST request to `/api/analyze` with:
- `file`: The document file
- `company_name`: Company name for the report

Example using curl:
```bash
curl -X POST -F "file=@document.pdf" -F "company_name=Example Corp" http://localhost:5000/api/analyze
```

## Project Structure

```
trendlyzer/
├── app/
│   ├── config/
│   │   └── config.py
│   ├── models/
│   │   └── report_metrics.py
│   ├── routes/
│   │   └── main.py
│   ├── services/
│   │   ├── email_service.py
│   │   ├── file_processor.py
│   │   └── report_generator.py
│   ├── static/
│   │   ├── fonts/
│   │   ├── images/
│   │   └── reports/
│   ├── templates/
│   │   ├── index.html
│   │   └── results.html
│   ├── utils/
│   │   └── text_processing.py
│   └── __init__.py
├── requirements.txt
├── run.py
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
