from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

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

responses.update({
    "✅ SMS Test Sent!": ["test sms", "send test sms", "test my sms"],
    "✅ Email Test Sent!": ["test email", "send test email", "test my email"],
    "Please enter your phone number to set up SMS.": ["set sms", "configure sms", "sms setup"],
    "Please enter your email configuration details.": ["set email", "configure email", "email setup"],
    "Rotating the servo...": ["rotate servo", "move servo", "servo rotate", "rotate servo motor"]
})


# Define helper functions for SMS, Email, and Servo commands
def load_settings():
    # This function should load the settings (e.g., from a file or database)
    return {}

def save_settings(settings):
    # This function should save the settings
    pass

# Define the main function to handle incoming user messages
def get_chatbot_response(user_message):
    user_message = user_message.strip().lower()

    # Email Configuration Commands
    if user_message.startswith("set email"):
        return "Please enter your email address using: email: your@email.com"

    if user_message.startswith("email:"):
        email = user_message.split(":", 1)[1].strip()
        settings = load_settings()
        settings["email"] = email
        save_settings(settings)
        return "Email saved. Now set SMTP server using: smtp: smtp.gmail.com"

    if user_message.startswith("smtp:"):
        smtp = user_message.split(":", 1)[1].strip()
        settings = load_settings()
        settings["smtp_server"] = smtp
        save_settings(settings)
        return "SMTP server saved. Now set port using: port: 587"

    if user_message.startswith("port:"):
        port = int(user_message.split(":", 1)[1].strip())
        settings = load_settings()
        settings["smtp_port"] = port
        save_settings(settings)
        return "SMTP port saved. Now enter your email password using: password: your_password"

    if user_message.startswith("password:"):
        password = user_message.split(":", 1)[1].strip()
        settings = load_settings()
        settings["email_password"] = password
        save_settings(settings)
        return "Password saved. Email configuration completed."

    # Test Email
    if user_message == "test email":
        send_email("Test Alert: Email integration successful.")
        return "✅ Email Test Sent!"

    # SMS Configuration
    if user_message.startswith("set sms"):
        return "Please provide your phone number using: phone number: <your_number>"

    if user_message.startswith("phone number"):
        phone_number = user_message.split(":")[1].strip()
        settings = load_settings()
        settings["phone_number"] = phone_number
        save_settings(settings)
        return "Phone number saved!"

    if user_message == "test sms":
        settings = load_settings()
        phone = settings.get("phone_number", "")
        if not phone:
            return "⚠️ Configure phone using: phone number: <number>"
        payload = {
            "api_key": "YOUR_BEAM_AFRICA_API_KEY",
            "to": phone,
            "message": "[Test] This is a test message from Smartfy IoT Chatbot.",
        }
        response = requests.post("YOUR_BEAM_AFRICA_ENDPOINT", data=payload)
        return "✅ SMS sent!" if response.status_code == 200 else "❌ Failed to send SMS"

    # Servo Commands
    if user_message.startswith("servo"):
        try:
            angle = int(user_message.split(" ")[1])
            if 0 <= angle <= 180:
                rotate_servo(angle)
                return f"✅ Rotating the servo to {angle}°."
            else:
                return "❌ Invalid servo angle. Use an angle between 0 and 180."
        except ValueError:
            return "❌ Invalid servo command. Use: servo <angle>"

    # General Response Lookup
    for response, keywords in responses.items():
        if any(keyword in user_message for keyword in keywords):
            return response

    return "❌ Sorry, I didn’t understand that. Type 'help' to see valid commands."
