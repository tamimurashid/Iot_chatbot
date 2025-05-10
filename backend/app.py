# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
from conf import *
from nlp_engine import *
from sms_handler import Send_sms
from db_config import *
from email_handler import send_email_notification
from bson import ObjectId
import json






app = Flask(__name__)
CORS(app)


with open("chatbot_message_response.json") as f:
    chatbot_messages = json.load(f)

pending_command = None
user_id = "default_user"

@app.route('/chat', methods=['POST'])
def chat():
    global pending_command
    data = request.get_json(force=True)
    user_message = str(data.get('message', '')).strip().lower()
    user_data = get_user(user_id)
    username = user_data.get("username")

   


    if user_message.startswith("quick setup"):
        return jsonify({
        "reply": f"Hello {username}, welcome to the quick setup for your device.\n"
                 "Please answer the following questions to complete the configuration.\n\n"
                 "1. Please enter a name for your device. Example:\n"
                 "   device name: Smart Controller"
    })

    if user_message.startswith("device name"):
       device_name = user_message.split(":", 1)[1].strip()
       update_user(user_id, {"device_name": device_name})
       return jsonify({
          "reply": f"Great, {username}! Your device name is now set to {device_name}.\n\n"       "Let's continue with the next alert configuration  step.\n" 
                      "Type Alert configuration or alert config to proccede with next step "
     })

    if any(user_message.startswith(prefix) for prefix in ["alert config", "alert configuration"]):
        alert_msg = chatbot_messages["alert_config"]
        reply = (
                alert_msg["title"] +
                "\n".join(alert_msg["points"]) + "\n\n" +
                alert_msg["sms_info"] + "\n\n" +
                alert_msg["email_info"]
            )
        return jsonify({"reply": reply})
            

        
        
    

    


    # Email Configuration Commands
    if user_message.startswith("set email"):
        return jsonify({"reply": "Please enter your email address using: email: your@email.com"})

    if user_message.startswith("email:"):
        email = user_message.split(":", 1)[1].strip()
        update_user(user_id, ({"email": email}))
        return jsonify({"reply": "Email saved. Now set SMTP server using: smtp: smtp.gmail.com"})

    if user_message.startswith("smtp:"):
        smtp = user_message.split(":", 1)[1].strip()
        update_user(user_id, {"smtp_server": smtp})
        return jsonify({"reply": "SMTP server saved. Now set port using: port: 587"})

    if user_message.startswith("port:"):
        port = int(user_message.split(":", 1)[1].strip())
        update_user(user_id, {"smtp_port": port})
        return jsonify({"reply": "SMTP port saved. Now enter your email password using: password: your_password"})

    if user_message.startswith("password:"):
        password = user_message.split(":", 1)[1].strip()
        update_user(user_id, {"email_password": password})
        return jsonify({"reply": "Password saved. Now configure the recipient email using .  recipient_email: your_recepient email"})
    
    if user_message.startswith("recipient_email:"):
        recipient_emails = user_message.split(":", 1)[1].strip()
        update_user(user_id, {"recipient_emails": recipient_emails})
        return jsonify({"reply": "Recipient emails saved. Email configuration completed."})

    # Test Email
    if user_message == "test email":
       return send_email_notification("Test Alert: Email integration successful.", user_id)


    # SMS Configuration
    if user_message.startswith("set sms"):
        return jsonify({"reply": "Please provide your phone number using: phone number: <your_number>"})

    if user_message.startswith("phone number"):
        phone_number = user_message.split(":")[1].strip()
        update_user(user_id, {"phone_number": phone_number})
        return jsonify({"reply": "Phone number saved!"})
    
    if user_message.startswith("test sms"):
        phone = user_data.get("phone_number")
        if not phone:
            return jsonify({"reply": "⚠️ Configure phone using: phone number: <number>"})
        
        # Beam Africa SMS API payload
        reply = Send_sms(phone, "Test Alert: SMS integration successfully!")

       # Handle ObjectId in the reply
        if isinstance(reply, dict):
            for key in reply:
                if isinstance(reply[key], ObjectId):
                    reply[key] = str(reply[key])

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
    user_data = get_or_create_user(user_id=user_id)

    if not user_data or "phone_number" not in user_data:
        return jsonify({"reply": "No phone configured"})

    phone = user_data["phone_number"]

    # Optional: Ensure ObjectId doesn't break JSON (in case you need it)
    if "_id" in user_data and isinstance(user_data["_id"], ObjectId):
        user_data["_id"] = str(user_data["_id"])

    reply = Send_sms(phone, "Test Alert: ✅ SMS integration successfully!")

    return jsonify({"reply": reply})
    


  
@app.route('/send_email', methods=['POST'])
def send_email():
    msg = request.json.get("message", "")
    return send_email_notification(msg, user_id)


@app.route('/command', methods=['GET'])
def get_command():
    global pending_command
    cmd = pending_command
    pending_command = None
    return jsonify({'command': cmd if cmd else ''})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
