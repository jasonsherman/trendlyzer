"""
Service for processing and analyzing content from uploaded files.
"""
import re
import os
import json_repair
import json
from flask import current_app
from openai import OpenAI
from dotenv import load_dotenv
from ..models.report_metrics import ReportMetrics
from ..services.report_generator import ReportGenerator
from ..services.email_service import send_report_email
from ..config.config import prompt1_user, prompt1_system


load_dotenv()

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
        "Message Count": 0
    }

def get_openai_client():
    """
    Initialize and return OpenAI client
    """
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        current_app.logger.debug("OpenAI client initialized successfully")
        return client
    except Exception as e:
        current_app.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        raise

def call_openai(client, user_prompt, system_prompt):
    try:
        completion = client.chat.completions.create(
            extra_body={},
            model="qwen/qwen3-235b-a22b:free",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        )
        if not completion:
            current_app.logger.error("OpenAI API returned None completion object")
            raise Exception("OpenAI API returned None completion object")

        if not completion.choices:
            current_app.logger.error(f"OpenAI API returned empty response: {str(completion)}")
            raise Exception("Empty response from OpenAI API")
        
        return completion.choices[0].message.content
    except Exception as e:
        current_app.logger.error(f"Error calling OpenAI API: {str(e)}")
        raise Exception(f"Failed to get response from OpenAI API: {str(e)}")
    
def extract_trimmed_json(response_json):
    return {
        "key_metrics": response_json.get("key_metrics", {}),
        "detailed_analysis": response_json.get("detailed_analysis", []),
        "recommendations": response_json.get("recommendations", [])
    }

def parse_openai_response(response_content):
    """
    Extract and parse the JSON object that follows the last `prefix` in the model output.
    Handles common noise like markdown fences or trailing commentary.
    """
    try:
        candidate = re.sub(r"```(?:json)?|```", "", response_content).strip()

        start = candidate.find("{")
        end   = candidate.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON braces found after prefix")

        json_str = candidate[start:end + 1]

        def _escaper(match):
            return match.group(0).replace("\n", "\\n")
        json_str = re.sub(r'"(?:[^"\\]|\\.)*"', _escaper, json_str, flags=re.DOTALL)

        return json_repair.loads(json_str)

    except Exception as e:
        current_app.logger.error(f"JSON parsing error: {e}")
        current_app.logger.debug(f"Original model output:\n{response_content}")
        raise

def process_conversations(lines: list, company_name: str) -> tuple:
    """Process conversation lines and extract relevant metrics and data.
    
    Args:
        lines: List of conversation lines
        company_name: Name of the company for keyword categorization
        
    Returns:
        tuple: (conversations, conv_data, all_keywords, top_keywords, theme_counts)
    """
    conversation_ids = []
    conversations = []
    current_conv_id = -1
    current_user = None
    current_conversation = ""

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

            conv_data[current_conv_id]["Message Count"] += 1

        else:
            if speaker != current_user:
                current_user = speaker
                current_conv_id += 1
                conversation_ids.append(current_conv_id)
                conversations.append(current_conversation)
                conv_data.append(create_conv_record(
                    current_conv_id, current_user))
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

            conv_data[current_conv_id]["Message Count"] += 1
                    
    return conversations, conv_data


def calculate_conversation_metrics(conv_data: list, total_conversations: int) -> tuple:
    """Calculate metrics from conversation data.
    
    Args:
        conv_data: List of conversation data dictionaries
        total_conversations: Total number of conversations
        
    Returns:
        tuple: (email_conversion_rate, phone_conversion_rate, follow_up_rate, 
                readiness_rate, lead_success_rate, trust_rate)
    """
    # Calculate lead success
    lead_success_count = sum(d["Lead Capture Success"] for d in conv_data)
    readiness_count = sum(d["Customer Readiness"] for d in conv_data)
    trust_count = sum(d["Trust Concerns"] for d in conv_data)

    lead_success_rate = (
        lead_success_count / total_conversations * 100) if total_conversations else 0
    readiness_rate = (
        readiness_count / total_conversations * 100) if total_conversations else 0
    trust_rate = (trust_count / total_conversations * 100) if total_conversations else 0

    # Calculate conversion rates
    email_leads = sum(d["Email Captured"] for d in conv_data)
    phone_leads = sum(d["Phone Captured"] for d in conv_data)
    followup_conv_count = sum(d["Follow‑up"] for d in conv_data)

    email_conversion_rate = (
        email_leads / total_conversations) * 100 if total_conversations else 0
    phone_conversion_rate = (
        phone_leads / total_conversations) * 100 if total_conversations else 0
    follow_up_rate = (
        followup_conv_count / total_conversations * 100) if total_conversations else 0
        
    return (email_conversion_rate, phone_conversion_rate, follow_up_rate,
            readiness_rate, lead_success_rate, trust_rate)

def has_meaningful_data(trimmed_json: dict) -> bool:
    """Check if the trimmed JSON contains meaningful data for visualization.
    
    Args:
        trimmed_json: The trimmed JSON response
        
    Returns:
        bool: True if there's meaningful data, False otherwise
    """
    # Check key_metrics
    metrics = trimmed_json.get("key_metrics", {})
    if any(metrics.get(category, []) for category in ["financial", "performance", "other_metrics"]):
        return True
        
    # Check detailed_analysis
    if trimmed_json.get("detailed_analysis", []):
        return True
        
    # Check recommendations
    if trimmed_json.get("recommendations", []):
        return True
        
    return False

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

    # Get AI analysis
    client = get_openai_client()
    user_prompt = prompt1_user.replace("{{DOCUMENT_CONTENT}}", content[:20000])
    ai_analysis = call_openai(client, user_prompt, prompt1_system)
   
    current_app.logger.info(f"AI analysis: {ai_analysis}")
    ai_analysis_json = parse_openai_response(ai_analysis)
    current_app.logger.info(f"=================================================")
    current_app.logger.info(f"=================================================")
    current_app.logger.info(f"=================================================")
    current_app.logger.info(f"PARSED AI analysis: {ai_analysis_json}")
    current_app.logger.info(f"=================================================")
    current_app.logger.info(f"=================================================")

    if mode == "Conversational Document":
        conversations, conv_data = process_conversations(lines, company_name)
        total_conversations = len(conversations)
        
        for d in conv_data:
            d["Lead Capture Success"] = d["Email Captured"] or d["Phone Captured"]
                    
        # Calculate metrics
        (email_conversion_rate, phone_conversion_rate, follow_up_rate,
         readiness_rate, lead_success_rate, trust_rate) = calculate_conversation_metrics(
            conv_data, total_conversations)

    else:
        email_conversion_rate = 0
        phone_conversion_rate = 0
        follow_up_rate = 0
        readiness_rate = 0
        lead_success_rate = 0
        trust_rate = 0
        total_conversations = 0
        conversations = []
        conv_data = []
        top_keywords = []

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
        mode=mode,
        ai_analysis=ai_analysis_json
    )

    current_app.logger.info(f"Metrics: {metrics}")

    report_generator = ReportGenerator(filename, company_name)
    report_path, overview = report_generator.generate(
        mode=mode,
        metrics=metrics,
    )
    key_topics = metrics.ai_analysis.get("key_topics", [])
    themes = metrics.ai_analysis.get("themes", [])


    
    # Send email with report
    send_report_email(report_path, company_name)
    
    return {
        'report_path': report_path,
        'overview': overview,
        'key_topics': key_topics,
        'themes': themes,
        'metrics': metrics
    } 