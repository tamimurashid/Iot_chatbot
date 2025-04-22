import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db import get_user_settings

def send_email(msg):
    settings = get_user_settings(device_id)  # Device ID must be passed
    to_email = settings.get("email")
    smtp_server = settings.get("smtp_server")
    smtp_port = settings.get("smtp_port")
    password = settings.get("email_password")
    
    if not all([to_email, smtp_server, smtp_port, password]):
        return "⚠️ Please configure email first."
    
    try:
        msg = MIMEMultipart()
        msg["From"] = to_email
        msg["To"] = to_email
        msg["Subject"] = "Smartfy IoT Notification"
        msg.attach(MIMEText(msg, "plain"))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(to_email, password)
            server.sendmail(to_email, to_email, msg.as_string())
        
        return f"✅ Email sent to {to_email}"
    except Exception as e:
        return f"❌ Failed to send email. Error: {str(e)}"

def configure_email(email_data):
    device_id = email_data.get('device_id')
    email = email_data.get('email')
    password = email_data.get('password')
    smtp_server = email_data.get('smtp_server')
    smtp_port = email_data.get('smtp_port')
    
    save_user_settings(device_id, email, password, None, smtp_server, smtp_port, None)
    return "✅ Email configured successfully"
