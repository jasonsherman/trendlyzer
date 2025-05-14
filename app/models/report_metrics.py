"""
Data models for the Trendlyzer application.
"""
from dataclasses import dataclass

@dataclass
class ReportMetrics:
    """Data class to hold report metrics."""
    word_count: int
    line_count: int
    total_conversations: int
    email_conversion_rate: float = 0.0
    phone_conversion_rate: float = 0.0
    follow_up_rate: float = 0.0
    readiness_rate: float = 0.0
    trust_rate: float = 0.0
    lead_success_rate: float = 0.0
    average_sentiment_score: float = 0.0
    mode: str = "Normal Document" 