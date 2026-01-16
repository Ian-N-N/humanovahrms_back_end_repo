import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from flask import current_app

logger = logging.getLogger(__name__)

def send_email(target_email, subject, text_content, html_content):
    """
    Sends an email using Brevo (formerly Sendinblue) API.
    """
    brevo_api_key = current_app.config.get('BREVO_API_KEY')
    sender_email = current_app.config.get('MAIL_DEFAULT_SENDER', 'austineochieng101@gmail.com')

    if not brevo_api_key:
        logger.warning("BREVO_API_KEY is missing. Email will NOT be sent.")
        print(f"--- MOCK EMAIL --- \nTo: {target_email}\nSubject: {subject}\n-----------------")
        return True

    try:
        # Configure API key authorization
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = brevo_api_key

        # Create an instance of the API class
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

        # Define the transactional email
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": target_email}],
            sender={"email": sender_email, "name": "HRMS Admin"},
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

        print(f"DEBUG: Attempting to send Brevo email from {sender_email} to {target_email}")
        api_response = api_instance.send_transac_email(send_smtp_email)
        
        logger.info(f"Email sent to {target_email} successfully. ID: {api_response.message_id}")
        print(f"DEBUG: Email sent successfully via Brevo. ID: {api_response.message_id}")
        return True
    except ApiException as e:
        logger.error(f"Brevo API Error: {str(e)}")
        print(f"DEBUG: Brevo Error details: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected Error sending email: {str(e)}")
        print(f"DEBUG: Unexpected Error: {str(e)}")
        return False

def send_onboarding_email(personal_email, work_email, password, name):
    subject = f"Welcome to the Team, {name}!"
    text_content = f"Hello {name},\n\nYour HRMS account is ready.\nEmail: {work_email}\nPassword: {password}\n\nURL: https://humanovahrms-front-end-repo.vercel.app/login"
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #2563eb;">Welcome to the Team, {name}!</h2>
        <p>Your HRMS account has been created successfully. You can now log in using the following credentials:</p>
        <div style="background-color: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Portal URL:</strong> <a href="https://humanovahrms-front-end-repo.vercel.app/login">https://humanovahrms-front-end-repo.vercel.app/login</a></p>
            <p><strong>Work Email:</strong> {work_email}</p>
            <p><strong>Default Password:</strong> <code style="background: #e5e7eb; padding: 2px 4px; border-radius: 4px;">{password}</code></p>
        </div>
        <p style="color: #6b7280; font-size: 0.875rem;">Please change your password after your first login for security purposes.</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
        <p>Best regards,<br /><strong>The Admin Team</strong></p>
    </div>
    """
    return send_email(personal_email, subject, text_content, html_content)

def send_leave_status_email(target_email, name, status, start_date, end_date):
    subject = f"Leave Request {status.capitalize()}"
    text_content = f"Hello {name},\n\nYour leave request for {start_date} to {end_date} has been {status}."
    
    color = "#16a34a" if status == 'approved' else "#dc2626"
    
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: {color};">Leave Request {status.capitalize()}</h2>
        <p>Hello <strong>{name}</strong>,</p>
        <p>Your recent leave request has been processed:</p>
        <div style="background-color: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Period:</strong> {start_date} to {end_date}</p>
            <p><strong>Status:</strong> <span style="color: {color}; font-weight: bold; text-transform: uppercase;">{status}</span></p>
        </div>
        <p>You can check the details in your dashboard portal.</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
        <p>Best regards,<br /><strong>The HR Team</strong></p>
    </div>
    """
    return send_email(target_email, subject, text_content, html_content)

def send_new_leave_request_notification(admins, employee_name, leave_type, start_date, end_date):
    """Notify Admin/HR of a new leave request submission via email."""
    subject = f"New Leave Request: {employee_name}"
    text_content = f"Hello Admin,\n\n{employee_name} has submitted a new {leave_type} request for {start_date} to {end_date}."
    
    html_content = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #2563eb;">New Leave Request Submission</h2>
        <p>A new leave request has been submitted for review:</p>
        <div style="background-color: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Employee:</strong> {employee_name}</p>
            <p><strong>Type:</strong> {leave_type.capitalize()}</p>
            <p><strong>Period:</strong> {start_date} to {end_date}</p>
        </div>
        <p>Please log in to the HR Portal to take action.</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
        <p>Best regards,<br /><strong>HRMS Automation</strong></p>
    </div>
    """
    
    success_count = 0
    for admin in admins:
        if admin.email:
            if send_email(admin.email, subject, text_content, html_content):
                success_count += 1
    return success_count
