import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

logger = logging.getLogger(__name__)

def send_onboarding_email(personal_email, work_email, password, name):
    """
    Sends an onboarding email using Gmail SMTP.
    Falls back to mock logging if MAIL_PASSWORD is missing.
    """
    smtp_server = current_app.config.get('MAIL_SERVER')
    smtp_port = current_app.config.get('MAIL_PORT')
    username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    sender_email = current_app.config.get('MAIL_DEFAULT_SENDER', username)

    # Verification Prints
    print(f"\n[DEBUG] SMTP Service Triggered for: {name}")
    print(f"[DEBUG] Target Personal Email: {personal_email}")
    print(f"[DEBUG] Sender Email (FROM): {sender_email}")
    
    if mail_password:
        masked_pwd = f"{mail_password[:2]}...{mail_password[-2:]}" if len(mail_password) > 4 else "****"
        print(f"[DEBUG] SMTP Password found: {masked_pwd}")
    else:
        print(f"[DEBUG] SMTP Password NOT FOUND in config.")

    subject = f"Welcome to the Team, {name}!"
    
    # Simple plain text version
    text_content = f"Hello {name},\n\nYour HRMS account is ready.\nEmail: {work_email}\nPassword: {password}\n\nURL: http://localhost:5173/login"

    # Brand-matched HTML Version
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #2563eb;">Welcome to the Team, {name}!</h2>
        <p>Your HRMS account has been created successfully. You can now log in using the following credentials:</p>
        <div style="background-color: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Portal URL:</strong> <a href="http://localhost:5173/login">http://localhost:5173/login</a></p>
            <p><strong>Work Email:</strong> {work_email}</p>
            <p><strong>Default Password:</strong> <code style="background: #e5e7eb; padding: 2px 4px; border-radius: 4px;">{password}</code></p>
        </div>
        <p style="color: #6b7280; font-size: 0.875rem;">Please change your password after your first login for security purposes.</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
        <p>Best regards,<br /><strong>The Admin Team</strong></p>
    </div>
    """

    if not mail_password:
        logger.warning("MAIL_PASSWORD is missing. Emails will NOT be sent.")
        print(f"--- MOCK EMAIL (NOT SENT) --- \nTo: {personal_email}\nSubject: {subject}\n-----------------")
        return True

    # Prepare message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = personal_email

    message.attach(MIMEText(text_content, "plain"))
    message.attach(MIMEText(html_content, "html"))

    try:
        # Connect to Gmail SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() # Secure the connection
            server.login(username, mail_password)
            server.sendmail(sender_email, personal_email, message.as_string())
        
        logger.info(f"Onboarding email sent to {personal_email} via Gmail SMTP.")
        print(f"[SUCCESS] Gmail SMTP accepted the email for {personal_email}")
        return True
    except Exception as e:
        logger.error(f"SMTP Error: {str(e)}")
        print(f"\n[CRITICAL] Gmail SMTP Failed!")
        print(f"Error: {str(e)}")
        print(f"HINT: Ensure 2-Step Verification is ON and you are using a 16-character 'App Password'.")
        return False
