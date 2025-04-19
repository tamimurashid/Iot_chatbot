# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)
CORS(app)

model = SentenceTransformer('all-MiniLM-L6-v2')

# Your possible responses and triggers
responses = {
    "✅ System is online and functioning properly.": ["status", "are you online", "is the system working", "system health", "check system status"],
    "🕒 Uptime: 2 hours 37 minutes.": ["uptime", "how long have you been running", "when did you start", "how long have you been active"],
    "🛠️ Here are some useful tools to control your IoT device...": ["tools", "control my device", "platforms", "iot tools", "suggest some tools", "device control options"],
    "🤖 Need a hand? You can ask me things like...": ["help", "what can you do", "i need help", "commands list", "how to use this chatbot", "assist me with commands"],
    "Hey there! 👋 I'm your Smartfy IoT Chatbot, here to help you interact with your smart system easily 🧠💡\n\nHere are some basic commands you can try:\n\n🔧 To rotate the servo motor to a specific angle (between 0° and 180°):\nType: servo 90 – This moves the servo to 90 degrees 🔄\nType: servo 0 – This resets it to 0 degrees 🔁\nType: servo 180 – This turns it fully to 180 degrees ↩️\n\n🦾 Use different angles to perform different object detection tasks:\nservo 45 – Great for scanning left 👈\nservo 90 – Center view 🎯\nservo 135 – Scan right 👉\n\n📦 More features coming soon! If you're not sure what to do, just ask for help at any time 😄\n\nReady when you are! 💬✨": ["about", "who are you", "what is smartfy", "about the bot", "what this system is all about", "I don't know how to use this chatbot, can I get assistance on basic commands on how to use it?"],
    "✅ Motion detected and alert received!": ["motion detected", "was there any movement", "did you detect any motion"],
    "❌ Invalid servo command. Use: servo <angle>": ["servo", "move servo", "rotate servo", "servo command"],
    "❌ Sorry, I didn’t understand that. Type 'help' to see valid commands.": ["unknown", "i don't understand", "invalid command", "what did you say", "unknown command"],
    "👋 Hello! How can I assist you today?": ["hi", "hello", "hey", "hi there", "hello bot", "hey bot", "greetings"],
    "Okay, I’m here to help. What can I do for you?": ["okay", "all right", "fine", "understood"],
    "🤔 Would you like me to assist you with basic commands or guide you through how to use this system?": ["can you assist", "how to use this chatbot", "basic commands help", "need help with usage"],
    "🕰️ You can set a time schedule for your device to be active. For example, 'Activate at 7:00 AM' or 'Deactivate at 10:00 PM.'": ["time schedule", "create time schedule", "set device schedule", "schedule activation", "schedule deactivation"],
}


# Precompute embeddings for known phrases
phrase_embeddings = []
reply_keys = []

for reply, phrases in responses.items():
    for phrase in phrases:
        phrase_embeddings.append(model.encode(phrase))
        reply_keys.append(reply)

phrase_embeddings = np.array(phrase_embeddings)

# For handling pending commands like servo
pending_command = None

@app.route('/chat', methods=['POST'])
def chat():
    global pending_command
    data = request.get_json(force=True)
    user_message = str(data.get('message', '')).strip().lower()

    # Handle direct command (servo)
    if user_message.startswith("servo"):
        try:
            angle = int(user_message.split()[1])
            pending_command = "servo " + str(angle)  # Replaced f-string with string concatenation
            return jsonify({"reply": "🦾 Servo will rotate to {}°".format(angle)})  # Replaced f-string with .format()
        except:
            return jsonify({"reply": "❌ Invalid servo command. Use: servo <angle>"})

    # Encode user input
    user_embedding = model.encode(user_message)

    # Compute similarity
    similarities = cosine_similarity([user_embedding], phrase_embeddings)[0]
    best_idx = np.argmax(similarities)

    # If similarity is above threshold, return best match
    if similarities[best_idx] > 0.6:
        reply = reply_keys[best_idx]
    else:
        reply = "❌ Sorry, I didn’t understand that. Type 'help' to see valid commands."

    return jsonify({'reply': reply})

@app.route('/command', methods=['GET'])
def get_command():
    global pending_command
    cmd = pending_command
    pending_command = None
    return jsonify({'command': cmd if cmd else ''})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
