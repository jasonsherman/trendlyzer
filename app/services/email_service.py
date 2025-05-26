"""
Service for handling email functionality.
"""
import os
import logging
from flask import current_app
from flask_mail import Message
from ..config.config import MAIL_CONFIG

logger = logging.getLogger(__name__)

def send_report_email(report_path: str, company_name: str) -> str:
    """Send report via email."""
    try:
        recipient_email = os.getenv("RECEIVER_MAIL")
        if not recipient_email:
            logger.error("RECEIVER_MAIL environment variable not set")
            return "Error: RECEIVER_MAIL not configured"

        if not os.getenv("MAIL_USERNAME") or not os.getenv("MAIL_PASSWORD"):
            logger.error("MAIL_USERNAME or MAIL_PASSWORD not configured")
            return "Error: Email credentials not configured"

        msg = Message(
            subject=f"Trendlyzer Report for {company_name}",
            recipients=[recipient_email],
            body=f"A Trendlyzer report for {company_name} was just analyzed!"
        )
        
        file_path = report_path.lstrip('/')
        if not os.path.exists(file_path):
            logger.error(f"Report file not found: {file_path}")
            return f"Error: Report file not found at {file_path}"

        with open(file_path, 'rb') as fp:
            msg.attach(
                filename=os.path.basename(file_path),
                content_type='application/pdf',
                data=fp.read()
            )
        
        logger.info(f"Attempting to send email to {recipient_email}")
        current_app.mail.send(msg)
        logger.info(f"Report sent successfully to {recipient_email}")
        return f"EMAIL sent to {recipient_email} with {report_path}"
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        logger.error(f"Mail config: {MAIL_CONFIG}")
        return f"Failed to send email: {str(e)}" 