from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(force=True)  # force=True ensures JSON is parsed even if header is wrong
    except Exception as e:
        return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid request, expected JSON with "message" key'}), 400

    user_message = str(data['message']).strip().lower()

    # Handle predefined command
    if user_message == 'help':
        reply = "💬 You can ask things like 'status', 'uptime', or 'about'."
    elif user_message == 'status':
        reply = "✅ System is online and functioning properly."
    elif user_message == 'uptime':
        reply = "🕒 Uptime: 2 hours 37 minutes."
    elif 'assit' in user_message:
        reply = "💬 You can ask things like 'status', 'uptime', or 'about'."
    elif user_message == 'about':
        reply = "🤖 I am a simple chatbot to help monitor your IoT project."

    # elif user_message == 'Ok' or 'Okay' or 'yes' or 'OKAY' or 'YES' or 'OK':
    #     reply = "Okay then,  please tell me what to do "    
    else:
        reply = "Sorry the chatbot is design only for monitoring your IoT project.Please ask help for more information."

    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)
