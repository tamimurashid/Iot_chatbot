from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

pending_command = None  # shared variable

@app.route('/chat', methods=['POST'])
def chat():
    global pending_command
    data = request.get_json(force=True)
    user_message = str(data.get('message', '')).strip().lower()

    if user_message == 'status':
        reply = "✅ System is online and functioning properly."
    elif user_message == 'uptime':
        reply = "🕒 Uptime: 2 hours 37 minutes."
    elif 'assist' in user_message or 'help' in user_message:
        reply = "💬 You can ask things like 'status', 'uptime', 'about', or 'servo <angle>'."

    elif 'about' in user_message or 'help' in user_message:
        reply = "💬 You can ask things like 'status', 'uptime', 'about', or 'servo <angle>'."

    elif user_message == 'about':
         reply = "🤖 I am a simple chatbot to help monitor your IoT project."
    elif user_message == 'motion detected':
        reply = "✅ Motion detected and alert received!"
    elif user_message.startswith('servo'):
        try:
            angle = int(user_message.split()[1])
            pending_command = f"servo {angle}"
            reply = f"🦾 Servo will rotate to {angle}°"
        except:
            reply = "❌ Invalid servo command. Use: servo <angle>"
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

