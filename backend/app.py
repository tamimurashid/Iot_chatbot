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

    elif 'tools' in user_message or 'control' in user_message:
        reply = "🛠️ Here are some useful tools and platforms to help you control your IoT device smoothly:\n\n" \
                "📱 Blynk App – Control devices via mobile app UI 📲\n" \
                "💬 Smartfy IoT Chatbot – Send text commands like `servo 90`, `status`, `about` 🤖\n" \
                "🧠 Flask Web Server – For handling backend logic and REST API requests 🌐\n" \
                "📡 ESP8266/ESP32 – Microcontrollers that connect your hardware to the internet 📶\n\n" \
                "Combine these tools for full control and automation of your smart system! 🚀"

    elif 'help' in user_message or 'help' in user_message:
        reply = "🤖 Need a hand? You can ask me things like:\n\n" \
                "🔹 'status' – Check system status ✅\n" \
                "🔹 'uptime' – See how long the system has been running ⏱️\n" \
                "🔹 'about' – Learn how to use this chatbot 📘\n" \
                "🔹 'servo <angle>' – Move the servo motor to any angle (0 to 180) 🔄\n\n" \
                "Just type any of those commands and I’ll respond! 🦾💬"
        
    elif 'about' in user_message or 'about' in user_message:
        reply = "💬 Smartfy IoT Chatbot is an intelligent assistant that enables real-time monitoring and control of IoT devices through simple chat commands. It bridges communication between users and smart systems via platforms like Telegram or web apps."
    
    elif 'assit' in user_message or 'assit' in user_message:
        reply = """Hey there! 👋 I'm your Smartfy IoT Chatbot, here to help you interact with your smart system easily 🧠💡

    Here are some basic commands you can try:

    🔧 To rotate the servo motor to a specific angle (between 0° and 180°):
    Type: servo 90 – This moves the servo to 90 degrees 🔄  
    Type: servo 0 – This resets it to 0 degrees 🔁  
    Type: servo 180 – This turns it fully to 180 degrees ↩️

    🦾 Use different angles to perform different object detection tasks:
    servo 45 – Great for scanning left 👈  
    servo 90 – Center view 🎯  
    servo 135 – Scan right 👉  

    📦 More features coming soon! If you're not sure what to do, just ask for help at any time 😄

    Ready when you are! 💬✨"""

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

