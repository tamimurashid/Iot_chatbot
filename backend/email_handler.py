import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db_config import load_settings
from flask import jsonify


def send_email_notification(message):
    settings = load_settings()
    to_email = settings.get("email")
    smtp_server = settings.get("smtp_server")
    smtp_port = settings.get("smtp_port")
    password = settings.get("email_password")

    if not all([to_email, smtp_server, smtp_port, password]):
        return jsonify({"reply": "⚠️ Please configure email first using: set email"})
        

    try:
        msg = MIMEMultipart()
        msg["From"] = to_email
        msg["To"] = to_email
        msg["Subject"] = "Smartfy IoT Notification"

        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(to_email, password)
            server.sendmail(to_email, to_email, msg.as_string())

        return jsonify({"reply": f"✅ Email sent to {to_email}"})

    except Exception as e:

        return jsonify({"reply": f"❌ Failed to send email. Error: {str(e)}"})
