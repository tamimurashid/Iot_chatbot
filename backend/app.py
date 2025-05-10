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
    data = request.get_json(force=True)
    user_message = str(data.get('message', '')).strip()
    user_id = str(data.get('user_id', 'default_user'))  # make sure this is provided
    user_data = get_user(user_id)
    username = user_data.get("username", "User")

    # ---------------- QUICK SETUP ---------------- #
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
            "reply": f"Great, {username}! Your device name is now set to {device_name}.\n\n"
                    #  "Let's continue with the next alert configuration step.\n"
                    #  "Type 'alert configuration' to proceed."
                    "Device model eg esp32 , es8266 or any device modal\n"
                     "Type device modal: esp32 , es8266 "
        })
    
    if user_message.startswith("device modal"):
        device_modal = user_message.split(":", 1)[1].strip()
        update_user(user_id, {"device_modal": device_modal})
        return jsonify({
            "reply": f"Great, {username}! Your device modal is now set to {device_modal}.\n\n"
                     "Let's continue with the next alert configuration step.\n"
                     "Type 'alert configuration' to proceed."
                   
        })

    # ---------------- ALERT CONFIG ---------------- #
    if any(user_message.startswith(prefix) for prefix in ["alert config", "alert configuration"]):
        alert_msg = chatbot_messages["alert_config"]
        reply = (
            alert_msg["title"] +
            "\n".join(alert_msg["points"]) + "\n\n" +
            alert_msg["sms_info"] + "\n\n" +
            alert_msg["email_info"]
        )
        return jsonify({"reply": reply})

    # ---------------- EMAIL CONFIG ---------------- #
    if user_message.startswith("set email"):
        return jsonify({"reply": "Enter your email using: email: your@email.com"})

    if user_message.startswith("email:"):
        return update_field(user_message, "email", user_id, "Email saved. Now set SMTP server using: smtp: smtp.gmail.com")

    if user_message.startswith("smtp:"):
        return update_field(user_message, "smtp_server", user_id, "SMTP server saved. Now set port using: port: 587")

    if user_message.startswith("port:"):
        port = int(user_message.split(":", 1)[1].strip())
        update_user(user_id, {"smtp_port": port})
        return jsonify({"reply": "SMTP port saved. Now enter your email password using: password: your_password"})

    if user_message.startswith("password:"):
        return update_field(user_message, "email_password", user_id, "Password saved. Now configure recipient email using: recipient_email: your_email")

    if user_message.startswith("recipient_email:"):
        return update_field(user_message, "recipient_emails", user_id, "Recipient email saved. Email configuration completed.")

    if any(user_message.startswith(prefix) for prefix in ["test email", "email test"]):
        return send_email_notification("Test Alert: Email integration successful.", user_id)

    # ---------------- SMS CONFIG ---------------- #
    if user_message.startswith("set sms"):
        return jsonify({"reply": "Enter your phone number using: phone number: <255xxxxxxx>"})

    if user_message.startswith("phone number"):
        return update_field(user_message, "phone_number", user_id, "Phone number saved! now add sms api key obtain from beam africa using: api key:<your api key>")
    
    if user_message.startswith("api key"):
        return update_field(user_message, "api_key", user_id, "api key saved! finish by adding beam africa secret key by using: secret key: <user secret key>")
    
    if user_message.startswith("secret key"):
        update_user(user_id, {"secret_key": user_message.split(":", 1)[1].strip()})
        return jsonify({
            "reply": "✅ Secret key saved successfully!\n\n"
                    "📡 SMS alert configuration completed.\n\n"
                    "📊 Next: Let's configure your **datastream**.\n\n"
                    "➡️ Use the format:\n"
                    "`datastream: parameter=temperature, type=float, virtualPin=V1`\n"
                    "`datastream: parameter=humidity, type=int, virtualPin=V2`\n\n"
                    "📝 Add as many datastreams as you want.\n"
                    "When done, type `start device` to generate a device ID and authentication token."
        })
        
        # ---------------- DATASTREAM CONFIG ---------------- #
    if user_message.startswith("datastream:"):
        try:
            parts = user_message.split(":", 1)[1].strip().split(",")
            ds_info = {}
            for item in parts:
                key, value = item.strip().split("=")
                ds_info[key.strip()] = value.strip()

            # Get existing datastreams, add new one
            existing = user_data.get("datastreams", [])
            existing.append(ds_info)
            update_user(user_id, {"datastreams": existing})

            return jsonify({
                "reply": f"✅ Datastream `{ds_info.get('parameter', 'unknown')}` saved successfully.\n"
                        f"Keep adding or type `start device` to finish setup."
            })
        except Exception:
            return jsonify({
                "reply": "⚠️ Invalid format. Use:\n"
                        "`datastream: parameter=temperature, type=float, virtualPin=V1`"
            })

    if user_message.strip().lower() == "start device":
        import secrets
        device_id = f"dev_{secrets.token_hex(4)}"
        auth_token = secrets.token_hex(16)
        update_user(user_id, {
            "device_id": device_id,
            "auth_token": auth_token
        })
        return jsonify({
            "reply": f"🚀 Device setup complete!\n\n"
                    f"🆔 Device ID: `{device_id}`\n"
                    f"🔑 Auth Token: `{auth_token}`\n\n"
                    f"✅ Use these in your ESP32 code to authenticate and send data securely."
        })
        

    if user_message == "test sms":
        phone = user_data.get("phone_number")
        if not phone:
            return jsonify({"reply": "⚠️ Configure phone using: phone number: <number>"})

        reply = Send_sms(phone, "Test Alert: SMS integration successful!")
        if isinstance(reply, dict):
            for key in reply:
                if isinstance(reply[key], ObjectId):
                    reply[key] = str(reply[key])
        return jsonify({"reply": reply})

    # ---------------- NLP FALLBACK ---------------- #
    reply_test = get_best_reply(user_message)
    return jsonify({"reply": reply_test})


# ---------------- Helper Function ---------------- #
def update_field(user_message, field_name, user_id, success_msg):
    try:
        value = user_message.split(":", 1)[1].strip()
        update_user(user_id, {field_name: value})
        return jsonify({"reply": success_msg})
    except Exception:
        return jsonify({"reply": f"⚠️ Invalid format. Please use: {field_name}: <value>"})


   

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
    

@app.route("/api/device/update", methods=["POST"])
def update_device_data():
    data = request.get_json()

    device_id = data.get("device_id")
    token = data.get("auth_token")
    pin = data.get("pin")
    parameter = data.get("parameter")
    value = data.get("value")

    # Step 1: Validate device
    device = db.devices.find_one({"device_id": device_id, "auth_token": token})
    if not device:
        return jsonify({"status": "error", "message": "Invalid device or token"}), 401

    # Step 2: Update datastream
    db.devices.update_one(
        {"device_id": device_id, "datastreams.pin": pin},
        {
            "$set": {
                "datastreams.$.latest_value": value,
                "datastreams.$.timestamp": datetime.utcnow()
            }
        }
    )

    return jsonify({"status": "success", "message": "Data updated"})

  
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
