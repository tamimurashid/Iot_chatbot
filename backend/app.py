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
    "✅ System is online and functioning properly.": ["status", "are you online", "is the system working", "system health"],
    "🕒 Uptime: 2 hours 37 minutes.": ["uptime", "how long have you been running", "when did you start"],
    "🛠️ Here are some useful tools to control your IoT device...": ["tools", "control my device", "platforms", "iot tools"],
    "🤖 Need a hand? You can ask me things like...": ["help", "what can you do", "i need help", "commands list"],
    "💬 Smartfy IoT Chatbot is an intelligent assistant...": ["about", "who are you", "what is smartfy", "about the bot"],
    "✅ Motion detected and alert received!": ["motion detected", "was there any movement"],
    "❌ Invalid servo command. Use: servo <angle>": ["servo", "move servo", "rotate servo"],
    "❌ Sorry, I didn’t understand that. Type 'help' to see valid commands.": ["unknown"]
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
