"""
Utility functions for text processing and analysis.
"""
import re
from typing import List, Counter
from nltk.corpus import stopwords
# from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)

def get_word_frequencies(text: str, top_n: int = 10) -> list:
    """Get word frequencies from text."""
    words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
    stop_words = set(stopwords.words('english'))
    filtered = [w for w in words if w not in stop_words and len(w) > 2]
    return Counter(filtered).most_common(top_n)



def contains_email(text: str) -> bool:
    """Detect if the text contains an email address."""
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return bool(match)

def contains_phone(text: str) -> bool:
    """Detect if the text contains a phone number."""
    match = re.search(r'(\+?\d[\d\s\-().]{7,}\d)', text)
    return bool(match)

def split_conversations(text: str) -> List[str]:
    """Split text into individual conversations."""
    parts = re.split(r'(?=^Agent:)', text, flags=re.MULTILINE)
    return [p.strip() for p in parts if p.strip()]

def categorize_keyword(kw: str, company_names: List[str], locations: List[str]) -> str:
    """Categorize a keyword based on predefined lists."""
    kw_lower = kw.lower()
    if kw_lower in company_names:
        return 'company name'
    elif kw_lower in locations:
        return 'location'
    return kw

