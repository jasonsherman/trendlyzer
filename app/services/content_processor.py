"""
Service for processing and analyzing content from uploaded files.
"""
import re
from collections import Counter
from typing import Dict, List, Tuple, Optional
from textblob import TextBlob
from flask import current_app
from ..models.report_metrics import ReportMetrics
from ..services.report_generator import ReportGenerator
from ..services.email_service import send_report_email
from ..utils.text_processing import (
    extract_keywords_tfidf,
    categorize_keyword,
    improved_theme_detection
)
from ..config.config import THEME_MAPPING

def create_conv_record(conv_id: int, user_name: str) -> dict:
    """Create a new conversation record."""
    return {
        "Conversation ID": conv_id,
        "User": user_name,
        "Email Captured": False,
        "Phone Captured": False,
        "Lead Capture Success": False,
        "Follow‑up": False,
        "Customer Readiness": False,
        "Trust Concerns": False,
        "Sentiment Score": 0.0,
        "Message Count": 0
    }

def process_content(content: str, filename: str, company_name: str) -> dict:
    """Process content and generate report data.
    
    Args:
        content: The text content to analyze
        filename: Name of the uploaded file
        company_name: Name of the company
        
    Returns:
        dict: Analysis results including metrics, keywords, and report path
    """
    word_count = len(content.split())
    line_count = len(content.splitlines())

    lines = [line.rstrip("\n") for line in content.splitlines()]
    # Detect if it's a conversational document
    has_agent = any(re.match(r"Agent:", line) for line in lines)
    has_other_speaker = any(re.match(
        r"[^:]{1,40}:", line) and not line.startswith("Agent:") for line in lines)
    mode = "Conversational Document" if has_agent and has_other_speaker else "Normal Document"

    conversation_ids = []
    conversations = []
    current_conv_id = -1
    current_user = None
    current_conversation = ""
    all_keywords = []

    email_pattern = re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    phone_pattern = re.compile(
        r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{3,4}[-.\s]?\d{0,4}")
    followup_keywords = re.compile(
        r"\b(follow up|schedule|demo|call|reach out|appointment|book)\b", re.IGNORECASE)
    readiness_keywords = re.compile(
        r"\b(buy|purchase|ready|interested|go ahead|sign me up|subscribe|order|start|proceed)\b", re.IGNORECASE)
    trust_keywords = re.compile(
        r"\b(scam|fake|trust|secure|safety|safe|legit|fraud|privacy|data leak|security)\b", re.IGNORECASE)

    conv_data = []

    # Parse the file to identify conversations and collect stats
    for line in lines:
        if not line.strip() or ":" not in line:
            continue  # skip empty and malformed lines
        speaker, message = [x.strip() for x in line.split(":", 1)]

        current_conversation += message

        if speaker == "Agent":
            # If no conversation started yet, skip until user speaks
            if current_conv_id < 0:
                continue
            # Follow‑up detection
            if followup_keywords.search(message):
                conv_data[current_conv_id]["Follow‑up"] = True

            # Sentiment for agent message
            conv_data[current_conv_id]["Sentiment Score"] += TextBlob(
                message).sentiment.polarity
            conv_data[current_conv_id]["Message Count"] += 1

        else:
            if speaker != current_user:
                current_user = speaker
                current_conv_id += 1
                conversation_ids.append(current_conv_id)
                conversations.append(current_conversation)
                conv_data.append(create_conv_record(
                    current_conv_id, current_user))

                keywords = extract_keywords_tfidf(current_conversation, top_n=5)
                convo_keywords = [categorize_keyword(kw, company_names=[company_name], locations=[]) for kw, _ in keywords]
                
                all_keywords.extend(convo_keywords)
                current_conversation = ""

            # Email / phone
            if email_pattern.search(message):
                conv_data[current_conv_id]["Email Captured"] = True
            if phone_pattern.search(message):
                nums = re.sub(
                    r"\D", "", phone_pattern.search(message).group())
                if len(nums) >= 7:
                    conv_data[current_conv_id]["Phone Captured"] = True
            # Readiness
            if readiness_keywords.search(message):
                conv_data[current_conv_id]["Customer Readiness"] = True

            # Trust concerns
            if trust_keywords.search(message):
                conv_data[current_conv_id]["Trust Concerns"] = True

            # Sentiment
            conv_data[current_conv_id]["Sentiment Score"] += TextBlob(
                message).sentiment.polarity
            conv_data[current_conv_id]["Message Count"] += 1

    top_keywords = Counter(all_keywords).most_common(10)
    theme_counts = {}
    for kw, count in top_keywords:
        for theme, keywords in THEME_MAPPING.items():
            if kw.lower() in keywords:
                theme_counts[theme] = theme_counts.get(
                    theme, 0) + count

    # For business docs, use improved theme detection
    if mode == "Conversational Document":
        total_conversations = len(conversations)
        for d in conv_data:
            d["Lead Capture Success"] = d["Email Captured"] or d["Phone Captured"]
            # Average sentiment
            if d["Message Count"]:
                d["Sentiment Score"] = round(
                    d["Sentiment Score"] / d["Message Count"], 3)
        # Aggregate metrics
        lead_success_count = sum(
            d["Lead Capture Success"] for d in conv_data)
        readiness_count = sum(d["Customer Readiness"]
                              for d in conv_data)
        trust_count = sum(d["Trust Concerns"] for d in conv_data)

        lead_success_rate = (
            lead_success_count / total_conversations * 100) if total_conversations else 0
        readiness_rate = (
            readiness_count / total_conversations * 100) if total_conversations else 0
        trust_rate = (trust_count / total_conversations *
                       100) if total_conversations else 0

        email_leads = sum(d["Email Captured"] for d in conv_data)
        phone_leads = sum(d["Phone Captured"] for d in conv_data)
        followup_conv_count = sum(d["Follow‑up"] for d in conv_data)

        email_conversion_rate = (
            email_leads / total_conversations) * 100 if total_conversations else 0
        phone_conversion_rate = (
            phone_leads / total_conversations) * 100 if total_conversations else 0
        follow_up_rate = (
            followup_conv_count / total_conversations * 100) if total_conversations else 0
        theme_counts_final = theme_counts
    else:
        email_conversion_rate = 0
        phone_conversion_rate = 0
        follow_up_rate = 0
        readiness_rate = 0
        lead_success_rate = 0
        trust_rate = 0
        total_conversations = 0
        theme_counts_final = improved_theme_detection(
            content, THEME_MAPPING, current_app.nlp)

    metrics = ReportMetrics(
        word_count=word_count,
        line_count=line_count,
        total_conversations=total_conversations,
        email_conversion_rate=round(email_conversion_rate, 2),
        phone_conversion_rate=round(phone_conversion_rate, 2),
        follow_up_rate=round(follow_up_rate, 2),
        readiness_rate=round(readiness_rate, 2),
        trust_rate=round(trust_rate, 2),
        lead_success_rate=round(lead_success_rate, 2),
        average_sentiment_score=round(sum(
            d["Sentiment Score"] for d in conv_data) / total_conversations, 3) if total_conversations else 0,
        mode=mode
    )

    report_generator = ReportGenerator(filename, company_name)
    report_path, overview = report_generator.generate(
        mode=mode,
        metrics=metrics,
        top_keywords=top_keywords,
        theme_counts=theme_counts_final,
        conversations=conversations,
        full_text=content
    )
    
    # Send email with report
    send_report_email(report_path, company_name)
    
    return {
        'report_path': report_path,
        'overview': overview,
        'top_keywords': top_keywords,
        'theme_counts': theme_counts_final,
        'metrics': metrics
    } 