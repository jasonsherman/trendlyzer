import os
import requests
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()


class ThemeAnalyzer:
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
                {"role": "system", "content": "You are an expert document analyzer that identifies key themes and topics in documents."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        return response.json()

    def analyze_themes(self, text: str) -> Dict[str, int]:
        """
        Analyze text for themes using AI

        Args:
            text (str): Input text to analyze

        Returns:
            dict: Dictionary containing theme counts
        """
        prompt = f"""
        Analyze the following document and identify the main themes/topics. For each theme, provide:
        1. The theme name
        2. A brief description of why it's relevant
        3. The number of times it appears in the text
        4. Key phrases or terms that indicate this theme

        Document:
        {text[:4000]}  # Limit content to avoid token limits

        Provide the analysis in this JSON format:
        {{
            "themes": [
                {{
                    "name": "theme name",
                    "description": "why this theme is relevant",
                    "count": number_of_occurrences,
                    "key_phrases": ["phrase1", "phrase2", ...]
                }}
            ]
        }}

        Focus on identifying themes that are actually present in the text, not just common business themes.
        """

        try:
            response = self._make_api_request(prompt)
            analysis = json.loads(response['choices'][0]['message']['content'])

            # Convert the themes list to a dictionary of theme counts
            theme_counts = {theme['name']: theme['count']
                            for theme in analysis.get('themes', [])}

            # Store the detailed theme information for later use
            self._last_theme_analysis = analysis.get('themes', [])

            return theme_counts
        except Exception as e:
            print(f"Error in theme analysis: {e}")
            return {}

    def get_theme_details(self) -> List[Dict[str, Any]]:
        """
        Get detailed information about the last analyzed themes

        Returns:
            list: List of dictionaries containing theme details
        """
        return getattr(self, '_last_theme_analysis', [])
