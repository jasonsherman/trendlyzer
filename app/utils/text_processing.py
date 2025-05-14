"""
Utility functions for text processing and analysis.
"""
import re
from typing import List, Tuple, Optional, Dict, Counter
from nltk.corpus import stopwords
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)

def get_word_frequencies(text: str, top_n: int = 10) -> list:
    """Get word frequencies from text."""
    words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
    stop_words = set(stopwords.words('english'))
    filtered = [w for w in words if w not in stop_words and len(w) > 2]
    return Counter(filtered).most_common(top_n)


def extract_keywords_tfidf(text: str, top_n: int = 5) -> List[Tuple[str, float]]:
    """Enhanced TF-IDF keyword extraction with additional preprocessing."""
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=top_n,
        ngram_range=(1, 2),
        strip_accents='unicode',
        lowercase=True
    )
    
    try:
        text = ' '.join(text.split())
        X = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = X.toarray()[0]
        keywords = list(zip(feature_names, scores))
        keywords.sort(key=lambda x: x[1], reverse=True)
        return keywords[:top_n]
    except Exception as e:
        logger.error(f"Error in TF-IDF keyword extraction: {e}")
        return []

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

def improved_theme_detection(text: str, theme_mapping: dict, nlp_model) -> dict:
    """Detect themes in text using spaCy's word vectors for semantic similarity.
    
    Args:
        text: The text to analyze
        theme_mapping: Dictionary mapping themes to their keywords
        nlp_model: Loaded spaCy model
        
    Returns:
        dict: Count of detected themes
    """
    doc = nlp_model(text)
    tokens = [
        token for token in doc if not token.is_stop and not token.is_punct and token.has_vector]
    theme_counts = {theme: 0 for theme in theme_mapping}
    for theme, keywords in theme_mapping.items():
        for kw in keywords:
            kw_vec = nlp_model(kw)[0]
            if not kw_vec.has_vector:
                continue
            # Count theme if any token in doc is similar to the keyword
            if any(kw_vec.similarity(token) > 0.75 for token in tokens):
                theme_counts[theme] += 1
    return {k: v for k, v in theme_counts.items() if v > 0}

def get_summary(text: str, max_sentences: int = 3) -> str:
    """Generate a concise summary of the text.
    
    Args:
        text: The text to summarize
        max_sentences: Maximum number of sentences in the summary
        
    Returns:
        str: A summary of the text
    """
    try:
        # Create TextBlob object
        blob = TextBlob(text)
        
        # Get sentences and their scores
        sentences = blob.sentences
        if not sentences:
            return "No content to summarize."
            
        # Score sentences based on word frequency
        word_freqs = Counter()
        for sentence in sentences:
            words = [word.lower() for word in sentence.words if len(word) > 2]
            word_freqs.update(words)
            
        # Calculate sentence scores
        sentence_scores = []
        for sentence in sentences:
            score = sum(word_freqs[word.lower()] for word in sentence.words if len(word) > 2)
            sentence_scores.append((sentence, score))
            
        # Get top sentences
        top_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:max_sentences]
        top_sentences.sort(key=lambda x: sentences.index(x[0]))  # Sort by original position
        
        # Combine sentences into summary
        summary = ' '.join(str(sentence[0]) for sentence in top_sentences)
        return summary
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return "Error generating summary." 