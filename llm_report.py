import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL = "meta-llama/llama-3-70b-instruct:free"


def generate_report_with_llm(document_text):
    prompt = f'''
You are an expert business analyst and report generator.

Given the following document content, generate a comprehensive, executive-style report. The report should include:

1. Executive Summary (concise, high-level overview)
2. Key Findings (main insights, trends, and patterns)
3. Detailed Analysis (in-depth breakdown of the content)
4. Recommendations (actionable suggestions)
5. Conclusion (summary and next steps)
6. Visualizations (charts/graphs as base64-encoded PNG images with captions)

For the Visualizations section:
- Analyze the data and suggest the most relevant charts (bar, pie, or line).
- For each chart, generate the chart as a base64-encoded PNG image and provide a descriptive caption.
- Return the chart images and captions in a JSON array.

Return your response in the following JSON format:

{{
  "executive_summary": "...",
  "key_findings": "...",
  "detailed_analysis": "...",
  "recommendations": "...",
  "conclusion": "...",
  "visualizations": [
    {{
      "caption": "Chart 1 description",
      "image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
    }}
  ]
}}

Here is the document content (truncated if very long):

{document_text[:4000]}
    '''
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert business analyst and report generator."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
