import os
import resend
from typing import List
from app.core.config import get_settings

class EmailService:
    def __init__(self):
        settings = get_settings()
        api_key = settings.RESEND_API_KEY
        if not api_key:
            print("Warning: RESEND_API_KEY is not set. Email sending will fail.")
        resend.api_key = api_key

    def send_welcome_email(self, to_email: str, user_name: str):
        """
        Send a welcome email when a user subscribes to their first alert.
        """
        try:
            params = {
                "from": "Alpha Calendar <onboarding@resend.dev>",
                "to": [to_email],
                "subject": "Welcome to Alpha Calendar Alerts",
                "html": f"""
                <h1>Welcome, {user_name}!</h1>
                <p>You have successfully subscribed to Alpha Calendar alerts.</p>
                <p>We will notify you when the Hype Score of your interested events spikes!</p>
                """
            }
            email = resend.Emails.send(params)
            print(f"Welcome email sent to {to_email}: {email}")
            return email
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
            return None

    def send_alert_email(self, to_emails: List[str], event_title: str, hype_score: int):
        """
        Send an alert email when Hype Score spikes.
        """
        try:
            params = {
                "from": "Alpha Calendar <alerts@resend.dev>",
                "to": to_emails,
                "subject": f"🔥 Hype Spike: {event_title} (Score: {hype_score})",
                "html": f"""
                <h1>Hype Alert!</h1>
                <p>The event <strong>{event_title}</strong> is heating up!</p>
                <p>Current Hype Score: <strong>{hype_score}</strong></p>
                <p><a href="http://localhost:3000">Check it out on Alpha Calendar</a></p>
                """
            }
            email = resend.Emails.send(params)
            print(f"Alert email sent to {len(to_emails)} recipients: {email}")
            return email
        except Exception as e:
            print(f"Failed to send alert email: {e}")
            return None

email_service = EmailService()
