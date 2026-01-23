import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
from backend.config import settings


# Carrier email-to-SMS gateways
CARRIER_GATEWAYS = {
    "verizon": "@vtext.com",
    "att": "@txt.att.net",
    "tmobile": "@tmomail.net",
    "sprint": "@messaging.sprintpcs.com",
}


class EmailSMSGateway:
    """Send SMS messages via email-to-SMS gateways (free alternative to Twilio)"""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password

    def send_sms(self, phone: str, carrier: str, message: str) -> Dict[str, any]:
        """
        Send SMS via email-to-SMS gateway.
        
        Args:
            phone: 10-digit phone number (e.g., "3605551234")
            carrier: Carrier name (e.g., "verizon", "att", "tmobile", "sprint")
            message: Message text (keep under 160 characters)
        
        Returns:
            {
                "success": bool,
                "error": str or None
            }
        """
        if carrier not in CARRIER_GATEWAYS:
            return {
                "success": False,
                "error": f"Unsupported carrier: {carrier}. Must be one of: {', '.join(CARRIER_GATEWAYS.keys())}"
            }

        # Construct SMS email address
        gateway = CARRIER_GATEWAYS[carrier]
        sms_email = f"{phone}{gateway}"

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = sms_email
            msg['Subject'] = ""  # Empty subject for SMS

            # Add message body
            msg.attach(MIMEText(message, 'plain'))

            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return {
                "success": True,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def test_connection(self) -> Dict[str, any]:
        """
        Test SMTP connection without sending a message.
        Useful for debugging email configuration.
        """
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)

            return {
                "success": True,
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def send_test_sms(self, phone: str, carrier: str) -> Dict[str, any]:
        """
        Send a test SMS to verify configuration.
        """
        test_message = "Test message from FishCatch AI Agent. If you received this, your SMS configuration is working!"
        return self.send_sms(phone, carrier, test_message)
