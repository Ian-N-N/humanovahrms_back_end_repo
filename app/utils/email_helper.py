import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to_email, subject, content):
    message = Mail(
        from_email=os.getenv('SENDGRID_FROM_EMAIL'),
        to_emails=to_email,
        subject=subject,
        html_content=content)
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        print(f"Failed to send email: {e}")
        return 500
