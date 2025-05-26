import os
import requests
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()


class AIAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "nvidia/llama-3.3-nemotron-super-49b-v1:free"

    def _make_api_request(self, prompt: str) -> Dict[str, Any]:
        """Make a request to OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert document analyzer that provides detailed insights about various types of documents."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        return response.json()

    def analyze_document(self, content: str, doc_type: str) -> Dict[str, Any]:
        """Analyze document content and return structured insights"""
        prompt = f"""
        Analyze the following {doc_type} document and provide detailed insights in JSON format:
        
        {content[:4000]}  # Limit content to avoid token limits
        
        Provide analysis in the following JSON structure:
        {{
            "document_type": "type of document",
            "key_topics": ["list of main topics"],
            "sentiment": "overall sentiment",
            "key_metrics": {{
                "financial": ["relevant financial metrics"],
                "performance": ["performance indicators"],
                "other": ["other important metrics"]
            }},
            "recommendations": ["list of actionable recommendations"],
            "visualization_suggestions": ["suggestions for charts/graphs"]
        }}
        """

        response = self._make_api_request(prompt)
        try:
            # Extract the JSON from the response
            analysis = json.loads(response['choices'][0]['message']['content'])
            return analysis
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return {}

    def generate_report_sections(self, content: str, doc_type: str) -> Dict[str, str]:
        """Generate detailed report sections using AI"""
        prompt = f"""
        Generate detailed report sections for this {doc_type} document:
        
        {content[:4000]}
        
        Provide the following sections in JSON format:
        {{
            "executive_summary": "brief overview",
            "key_findings": "main findings",
            "detailed_analysis": "in-depth analysis",
            "recommendations": "actionable recommendations",
            "conclusion": "concluding remarks"
        }}
        """

        response = self._make_api_request(prompt)
        try:
            sections = json.loads(response['choices'][0]['message']['content'])
            return sections
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return {}

    def suggest_visualizations(self, content: str, doc_type: str) -> List[Dict[str, Any]]:
        """Suggest appropriate visualizations based on document content"""
        prompt = f"""
        Suggest appropriate visualizations for this {doc_type} document:
        
        {content[:4000]}
        
        Provide suggestions in JSON format:
        {{
            "visualizations": [
                {{
                    "type": "chart type",
                    "title": "chart title",
                    "data_points": ["suggested data points"],
                    "purpose": "why this visualization is useful"
                }}
            ]
        }}
        """

        response = self._make_api_request(prompt)
        try:
            suggestions = json.loads(
                response['choices'][0]['message']['content'])
            return suggestions.get('visualizations', [])
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return []
