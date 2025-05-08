import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db_config import get_user
from flask import jsonify

def send_email_notification(message, user_id="default_user"):
    user_settings = get_user(user_id)

    if not user_settings:
        return jsonify({"reply": "⚠️ User settings not found. Please configure email first using: set email"})

    to_email = user_settings.get("email")
    smtp_server = user_settings.get("smtp_server")
    smtp_port = user_settings.get("smtp_port")
    password = user_settings.get("email_password")
    recipient_emails = user_settings.get("recipient_emails")

    if not all([to_email, smtp_server, smtp_port, password]):
        return jsonify({"reply": "⚠️ Incomplete email configuration. Please update your settings."})

    try:
        msg = MIMEMultipart()
        msg["From"] = to_email
        msg["To"] = recipient_emails
        msg["Subject"] = "Smartfy IoT Notification"
        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(to_email, password)
            server.sendmail(to_email, recipient_emails, msg.as_string())

        return jsonify({"reply": f"✅ Email sent to {recipient_emails}"})

    except Exception as e:
        return jsonify({"reply": f"❌ Failed to send email. Error: {str(e)}"})
