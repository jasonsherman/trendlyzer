# 📄 Trendlyzer – AI-Driven Document Analyzer & Report Generator

Upload files → Analyze Data → Extract Insights → Generate Beautiful PDF Reports. Try it live at [trendlyzer.com](https://trendlyzer.com)!


---

## ✨ Project Overview

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

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file based on `.env.example`:
```bash
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_API_KEY=your_supabase_api_key
```

### 4. Run the App
```bash
python run.py
```
Then open `http://localhost:5000` in your browser.

---

## 🔐 Privacy and Security

- Uploaded files are temporarily stored in Supabase and auto-deleted within 24 hours.
- Environment variables are used to secure access keys.
- No personal data is stored long-term.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙌 Contributions Welcome!

Feel free to open issues, suggest new features, or submit pull requests.  
Let's make data analysis faster, smarter, and more accessible together!

**Note:** To install Supabase support manually on Python 3.12, run:
pip install git+https://github.com/supabase-community/supabase-py.git
