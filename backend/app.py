# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from conf import *
from nlp_engine import *
from sms_handler import Send_sms
from db_config import save_settings, load_settings



app = Flask(__name__)
CORS(app)





pending_command = None

@app.route('/chat', methods=['POST'])
def chat():
    global pending_command
    data = request.get_json(force=True)
    user_message = str(data.get('message', '')).strip().lower()


    # Email Configuration Commands
    if user_message.startswith("set email"):
        return jsonify({"reply": "Please enter your email address using: email: your@email.com"})

    if user_message.startswith("email:"):
        email = user_message.split(":", 1)[1].strip()
        settings = load_settings()
        settings["email"] = email
        save_settings(settings)
        return jsonify({"reply": "Email saved. Now set SMTP server using: smtp: smtp.gmail.com"})

    if user_message.startswith("smtp:"):
        smtp = user_message.split(":", 1)[1].strip()
        settings = load_settings()
        settings["smtp_server"] = smtp
        save_settings(settings)
        return jsonify({"reply": "SMTP server saved. Now set port using: port: 587"})

    if user_message.startswith("port:"):
        port = int(user_message.split(":", 1)[1].strip())
        settings = load_settings()
        settings["smtp_port"] = port
        save_settings(settings)
        return jsonify({"reply": "SMTP port saved. Now enter your email password using: password: your_password"})

    if user_message.startswith("password:"):
        password = user_message.split(":", 1)[1].strip()
        settings = load_settings()
        settings["email_password"] = password
        save_settings(settings)
        return jsonify({"reply": "Password saved. Email configuration completed."})

    # Test Email
    if user_message == "test email":
        return send_email_notification("Test Alert: Email integration successful.")

    # SMS Configuration
    if user_message.startswith("set sms"):
        return jsonify({"reply": "Please provide your phone number using: phone number: <your_number>"})

    if user_message.startswith("phone number"):
        phone_number = user_message.split(":")[1].strip()
        settings = load_settings()
        settings["phone_number"] = phone_number
        save_settings(settings)
        return jsonify({"reply": "Phone number saved!"})
    
    if user_message.startswith("test sms"):
        settings = load_settings()
        phone = settings.get("phone_number", "")
        if not phone:
            return jsonify({"reply": "⚠️ Configure phone using: phone number: <number>"})
        
        # Beam Africa SMS API payload
        reply  = Send_sms(phone,  "Test Alert:  ✅  SMS integration successfully! ")
        return jsonify({"reply": reply})
        
        # this runs nlp if no custom command found 
    reply_test = get_best_reply(user_message)

    return jsonify({"reply": reply_test})


   

    # Servo command
    if user_message.startswith("servo"):
        try:
            angle = int(user_message.split()[1])
            pending_command = "servo " + str(angle)
            return jsonify({"reply": f"🦾 Servo will rotate to {angle}°"})
        except:
            return jsonify({"reply": "❌ Invalid servo command. Use: servo <angle>"})

@app.route('/send_sms', methods=['POST'])
def send_sms():
    settings = load_settings()
    phone = settings.get("phone_number")
    if not phone:
        return jsonify({"reply": "No phone configured"})
    
    reply  = Send_sms(phone,  "Test Alert:  ✅  SMS integration successfully! ")
    return jsonify({"reply": reply})
    


  
@app.route('/send_email', methods=['POST'])
def send_email():
    msg = request.json.get("message", "")
    return send_email_notification(msg)

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

@app.route('/command', methods=['GET'])
def get_command():
    global pending_command
    cmd = pending_command
    pending_command = None
    return jsonify({'command': cmd if cmd else ''})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
