import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import re


class KeywordExtractor:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

        self.stop_words = set(stopwords.words('english'))
        self.model = None  # Placeholder for any future ML model integration

    def extract_keywords(self, text, top_n=10):
        """
        Extract top keywords from text using frequency analysis

        Args:
            text (str): Input text to analyze
            top_n (int): Number of top keywords to return

        Returns:
            list: List of tuples containing (keyword, frequency)
        """
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)

        # Tokenize and remove stopwords
        words = word_tokenize(text)
        words = [
            word for word in words if word not in self.stop_words and len(word) > 2]

        # Count word frequencies
        word_freq = Counter(words)

        # Return top N keywords
        return word_freq.most_common(top_n)

    def analyze_text(self, text):
        """
        Analyze text and return keyword statistics

        Args:
            text (str): Input text to analyze

        Returns:
            dict: Dictionary containing keyword analysis results
        """
        keywords = self.extract_keywords(text)

        return {
            'top_keywords': keywords,
            'total_keywords': len(keywords),
            'keyword_density': len(keywords) / len(text.split()) if text else 0
        }
