from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')


# Predefined responses and NLP setup
responses = {
    "✅ System is online and functioning properly.": ["status", "are you online", "is the system working", "system health", "check system status"],
    "🕒 Uptime: 2 hours 37 minutes.": ["uptime", "how long have you been running", "when did you start", "how long have you been active"],
    "🛠️ Here are some useful tools to control your IoT device...": ["tools", "control my device", "platforms", "iot tools", "suggest some tools", "device control options"],
    "🤖 Need a hand? You can ask me things like...\n\n• help/sms – How to set up and test SMS alerts\n• help/email – How to set up email notifications\n• help/servo – Servo command guide\n• help/schedule – How to schedule device activity\n\nTry typing any of these help commands to get specific guidance.": ["help", "what can you do", "i need help", "commands list", "how to use this chatbot", "assist me with commands"],

    "📩 SMS Setup Help:\n\nTo configure and test SMS:\n1. set sms → Begin SMS setup\n2. phone number: +2557xxxxxxx → Save your phone\n3. test sms → Send a test alert message\n\nMake sure your device is online and the API key is valid.": ["help/sms", "sms help", "how to configure sms", "set up sms", "sms configuration"],

    "📧 Email Setup Help:\n\nTo configure sender email for alerts:\n1. set email → Start setup\n2. email: example@gmail.com → Enter sender email\n3. smtp: smtp.gmail.com → Set SMTP server\n4. port: 587 → Enter port (587 for TLS)\n5. password: your_app_password → Use your app password\n6. Then configure receiver email\nEnter receiver_email: receiver@gmail.com  \n\nYou can test it using:\ntest email → Sends a test email to the configured address.\n\nNote: It very important to  add sender (email that will be used for sending alert ) and recipient emails(email to receive alerts) here inorder to get alert and info through emails .": ["help/email", "email help", "how to configure email", "set up email", "email configuration", "how to use email", "email setup guide"],

    "✅ Motion detected and alert received!": ["motion detected", "was there any movement", "did you detect any motion"],
    "❌ Invalid servo command. Use: servo <angle>": ["servo", "move servo", "rotate servo", "servo command"],
    "❌ Sorry, I didn’t understand that. Type 'help' to see valid commands.": ["unknown", "i don't understand", "invalid command", "what did you say", "unknown command"],
    "👋 Hello! How can I assist you today?": ["hi", "hello", "hey", "hi there", "hello bot", "hey bot", "greetings"],
    "Okay, I’m here to help. What can I do for you?": ["okay", "all right", "fine", "understood"],
    "🤔 Would you like me to assist you with basic commands or guide you through how to use this system?": ["can you assist", "how to use this chatbot", "basic commands help", "need help with usage"],
    "🕰️ You can set a time schedule for your device to be active. For example, 'Activate at 7:00 AM' or 'Deactivate at 10:00 PM.'": ["time schedule", "create time schedule", "set device schedule", "schedule activation", "schedule deactivation"],
    "🔧 Servo Command Help:\nUse the format: servo <angle>\n\nExamples:\nservo 0 – Reset position\nservo 90 – Centered view\nservo 180 – Full right\n\nCommon angles:\nservo 45 – Left scan\nservo 135 – Right scan": ["help/servo", "servo help", "servo usage", "servo guide", "servo control instructions"],
    "Hey there! 👋 I'm your Smartfy IoT Chatbot, here to help you interact with your smart system easily 🧠💡\n\nHere are some basic commands you can try:\n\n🔧 To rotate the servo motor to a specific angle (between 0° and 180°):\nType: servo 90 – This moves the servo to 90 degrees 🔄\nType: servo 0 – This resets it to 0 degrees 🔁\nType: servo 180 – This turns it fully to 180 degrees ↩️\n\n🦾 Use different angles to perform different object detection tasks:\nservo 45 – Great for scanning left 👈\nservo 90 – Center view 🎯\nservo 135 – Scan right 👉\n\n🌡️ To check environmental readings:\nType: temp – Check current temperature 🌞\nType: humid – Check humidity level 💧\nType: rain – Check for rain detection 🌧️\nType: smoke – Check for smoke levels 🚬\n\n📢 Alerts and Notifications:\nType: alert sms – Get critical alerts via SMS 📲\nType: alert email – Receive alerts through email 📧\nType: alert status – Check which alert system is currently active ⚠️\n\n📦 More features coming soon! If you're not sure what to do, just ask for help at any time 😄\n\nReady when you are! 💬✨"
    : [
        "about", "who are you", "what is smartfy", "about the bot", "what this system is all about", "I don't know how to use this chatbot, can I get assistance on basic commands on how to use it?"
    ],
    "📅 Schedule Help:\nYou can set schedules like:\n- Activate at 7:00 AM\n- Deactivate at 10:00 PM\n\nMore advanced scheduling features coming soon!": ["help/schedule", "schedule help", "usage of schedule", "how to create schedule", "time schedule guide"],

    "Hello there!  Welcome to Smartfy IoT Chatbot . Here’s a quick guide on how to set up your chatbot 🛠️.\n\nThere are three phases in the device setup . Please select one by one to complete your device configuration :\n\n📌 You can begin by typing one of the following commands: [\"quick setup\", \"alert config\", \"datastream config\"\n\n🚀 1. Quick Setup:\n- Provide your device name 📱 and receiver email 📧.\n- This helps the chatbot identify and communicate with your device.\n\n📡 2. Alert Setup:\n- Uses default SMS configuration via Beam Africa API 📲 (charges may apply 💵).\n- You can customize your SMS settings and use your own sender email ✉️.\n\n📊 3. Datastream Configuration:\n- Define how data flows between your device and the chatbot 🔄.\n- For example:\n  🌡️ Temperature → v1\n  💧 Humidity → v2\n  📈 ...and so on\n\n🔐 After finishing configuration, the chatbot will generate:\n- Your User ID 🆔\n- An Authentication Token 🛡️\n\n📎 You’ll also receive a GitHub link 🔗 to download the library and get started coding 💻.\n\nLet’s build something smart! 💡": [
    "start", "device configuration", "device config", "config", "how to start", "how to create schedule", "time schedule guide"
  ],
  "📊 Datastream Configuration Guide\n\nHello there! Let's configure your Datastreams for your device. Datastreams define the data your IoT device will send or receive, such as temperature, humidity, or other sensor data.\n\n🚀 Example Command:\n`datastream: parameter=temperature, type=float, virtualPin=V1`\n\n🔧 Parameters Explained:\n- parameter: The name of your data (e.g., temperature, humidity).\n- type: Data type (e.g., float, int, string).\n- virtualPin: Virtual pin or identifier used by your platform (e.g., V1, V2).\n\n💡 You can add multiple datastreams by sending the command again with different parameters.\n\n✅ Once all datastreams are added, type `start device` to complete your setup.\n\n📎 Example Commands:\n- `datastream: parameter=humidity, type=float, virtualPin=V2`\n- `datastream: parameter=motion, type=bool, virtualPin=V3`\n\nLet's make your device smart and connected! 🤖✨": [
    "datastream", "help datastream", "what is datastream", "datastream config"
]

    


}


phrase_embeddings = []
reply_keys = []
for reply, phrases in responses.items():
    for phrase in phrases:
        phrase_embeddings.append(model.encode(phrase))
        reply_keys.append(reply)
phrase_embeddings = np.array(phrase_embeddings)