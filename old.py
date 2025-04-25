# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

model = SentenceTransformer('all-MiniLM-L6-v2')

# Beam Africa SMS API Configuration
BEAM_AFRICA_API_KEY = 'ab775ace75460c6c'
BEAM_AFRICA_ENDPOINT = 'https://apisms.beem.africa/v1/send'

# Load and save settings
def save_settings(settings):
    try:
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

def load_settings():
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Predefined responses and NLP setup
responses = {
    "✅ System is online and functioning properly.": ["status", "are you online", "is the system working", "system health", "check system status"],
    "🕒 Uptime: 2 hours 37 minutes.": ["uptime", "how long have you been running", "when did you start", "how long have you been active"],
    "🛠️ Here are some useful tools to control your IoT device...": ["tools", "control my device", "platforms", "iot tools", "suggest some tools", "device control options"],
    "🤖 Need a hand? You can ask me things like...\n\n• help/sms – How to set up and test SMS alerts\n• help/email – How to set up email notifications\n• help/servo – Servo command guide\n• help/schedule – How to schedule device activity\n\nTry typing any of these help commands to get specific guidance.": ["help", "what can you do", "i need help", "commands list", "how to use this chatbot", "assist me with commands"],

    "📩 SMS Setup Help:\n\nTo configure and test SMS:\n1. set sms → Begin SMS setup\n2. phone number: +2557xxxxxxx → Save your phone\n3. test sms → Send a test alert message\n\nMake sure your device is online and the API key is valid.": ["help/sms", "sms help", "how to configure sms", "set up sms", "sms configuration"],

    "📧 Email Setup Help:\n\nTo configure email alerts:\n1. set email → Start setup\n2. email: example@gmail.com → Enter sender email\n3. smtp: smtp.gmail.com → Set SMTP server\n4. port: 587 → Enter port (587 for TLS)\n5. password: your_app_password → Use your app password\n\nYou can test it using:\ntest email → Sends a test email to the configured address.\n\nNote: Add sender (your email) and recipient emails in the backend code.": ["help/email", "email help", "how to configure email", "set up email", "email configuration", "how to use email", "email setup guide"],

    "✅ Motion detected and alert received!": ["motion detected", "was there any movement", "did you detect any motion"],
    "❌ Invalid servo command. Use: servo <angle>": ["servo", "move servo", "rotate servo", "servo command"],
    "❌ Sorry, I didn’t understand that. Type 'help' to see valid commands.": ["unknown", "i don't understand", "invalid command", "what did you say", "unknown command"],
    "👋 Hello! How can I assist you today?": ["hi", "hello", "hey", "hi there", "hello bot", "hey bot", "greetings"],
    "Okay, I’m here to help. What can I do for you?": ["okay", "all right", "fine", "understood"],
    "🤔 Would you like me to assist you with basic commands or guide you through how to use this system?": ["can you assist", "how to use this chatbot", "basic commands help", "need help with usage"],
    "🕰️ You can set a time schedule for your device to be active. For example, 'Activate at 7:00 AM' or 'Deactivate at 10:00 PM.'": ["time schedule", "create time schedule", "set device schedule", "schedule activation", "schedule deactivation"],
    "🔧 Servo Command Help:\nUse the format: servo <angle>\n\nExamples:\nservo 0 – Reset position\nservo 90 – Centered view\nservo 180 – Full right\n\nCommon angles:\nservo 45 – Left scan\nservo 135 – Right scan": ["help/servo", "servo help", "servo usage", "servo guide", "servo control instructions"],
    "Hey there! 👋 I'm your Smartfy IoT Chatbot, here to help you interact with your smart system easily 🧠💡\n\nHere are some basic commands you can try:\n\n🔧 To rotate the servo motor to a specific angle (between 0° and 180°):\nType: servo 90 – This moves the servo to 90 degrees 🔄\nType: servo 0 – This resets it to 0 degrees 🔁\nType: servo 180 – This turns it fully to 180 degrees ↩️\n\n🦾 Use different angles to perform different object detection tasks:\nservo 45 – Great for scanning left 👈\nservo 90 – Center view 🎯\nservo 135 – Scan right 👉\n\n📦 More features coming soon! If you're not sure what to do, just ask for help at any time 😄\n\nReady when you are! 💬✨": [
        "about", "who are you", "what is smartfy", "about the bot", "what this system is all about", "I don't know how to use this chatbot, can I get assistance on basic commands on how to use it?"
    ],
    "📅 Schedule Help:\nYou can set schedules like:\n- Activate at 7:00 AM\n- Deactivate at 10:00 PM\n\nMore advanced scheduling features coming soon!": ["help/schedule", "schedule help", "usage of schedule", "how to create schedule", "time schedule guide"]

}


phrase_embeddings = []
reply_keys = []
for reply, phrases in responses.items():
    for phrase in phrases:
        phrase_embeddings.append(model.encode(phrase))
        reply_keys.append(reply)
phrase_embeddings = np.array(phrase_embeddings)

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
        payload = {
            "api_key": BEAM_AFRICA_API_KEY,
            "to": phone,
            "message": "[Test] This is a test message from Smartfy IoT Chatbot.",
        }
        response = requests.post(BEAM_AFRICA_ENDPOINT, data=payload)
        return jsonify({"reply": f"{'✅ SMS sent!' if response.status_code == 200 else '❌ Failed to send SMS.'}"})

    # Servo command
    if user_message.startswith("servo"):
        try:
            angle = int(user_message.split()[1])
            pending_command = "servo " + str(angle)
            return jsonify({"reply": f"🦾 Servo will rotate to {angle}°"})
        except:
            return jsonify({"reply": "❌ Invalid servo command. Use: servo <angle>"})

    # NLP response
    user_embedding = model.encode(user_message)
    similarities = cosine_similarity([user_embedding], phrase_embeddings)[0]
    best_idx = np.argmax(similarities)

    reply = reply_keys[best_idx] if similarities[best_idx] > 0.6 else \
            "❌ Sorry, I didn’t understand that. Type 'help' to see valid commands."

    return jsonify({'reply': reply})

@app.route('/send_sms', methods=['POST'])
def send_sms():
    settings = load_settings()
    phone = settings.get("phone_number")
    if not phone:
        return jsonify({"reply": "Please configure your phone number first."})
    msg = request.json.get("message", "")
    payload = {
        "api_key": BEAM_AFRICA_API_KEY,
        "to": phone,
        "message": msg,
    }
    response = requests.post(BEAM_AFRICA_ENDPOINT, data=payload)
    return jsonify({"reply": "✅ SMS sent!" if response.status_code == 200 else "❌ SMS failed!"})

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
