import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os


class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_report(self, to_email, report_path, company_name):
        """
        Send the generated report via email

        Args:
            to_email (str): Recipient email address
            report_path (str): Path to the report file
            company_name (str): Name of the company

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = f"Trendlyzer Report for {company_name}"

            # Add body
            body = f"""
            Hello,

            Please find attached the Trendlyzer report for {company_name}.

            Best regards,
            Trendlyzer Team
            """
            msg.attach(MIMEText(body, 'plain'))

            # Add attachment
            with open(report_path, 'rb') as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment',
                                  filename=os.path.basename(report_path))
                msg.attach(attach)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
